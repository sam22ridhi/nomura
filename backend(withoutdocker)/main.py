from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import httpx
import uuid
import logging

# Import our modules
from config_no_docker import *
from redis_models_no_docker import RedisUser, RedisSession, get_user_count, get_active_sessions_count, test_redis_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="WaveAI API - No Docker",
    version="1.0.0",
    description="Hackathon-ready authentication with local Redis"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_session_token(user_id: str, request: Request = None) -> str:
    """Create session token and store in Redis"""
    token = str(uuid.uuid4())
    expires_at = (datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).isoformat()
    
    user_agent = request.headers.get("user-agent") if request else None
    ip_address = request.client.host if request else None
    
    session = RedisSession(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address
    )
    session.save()
    
    return token

def get_user_from_token(token: str) -> Optional[RedisUser]:
    """Get user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id:
            return RedisUser.find_by_id(user_id)
        return None
    except JWTError:
        return None

async def get_current_user(request: Request) -> RedisUser:
    """Get current authenticated user"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No valid authorization header")
    
    token = auth_header.split(" ")[1]
    user = get_user_from_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    
    return user

def create_auth_response(user: RedisUser, request: Request = None) -> dict:
    """Create authentication response"""
    jwt_token = create_access_token(data={
        "sub": user.email,
        "user_id": user.id,
        "role": user.role
    })
    
    session_token = create_session_token(user.id, request)
    
    user.last_login = datetime.utcnow().isoformat()
    user.save()
    
    return {
        "access_token": jwt_token,
        "session_token": session_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        "user": user.to_dict()
    }

# Routes
@app.get("/")
async def root():
    redis_status = "✅ Connected" if test_redis_connection() else "❌ Disconnected"
    
    return {
        "message": "WaveAI API with Local Redis is running! 🌊",
        "status": "healthy",
        "redis_status": redis_status,
        "users_count": get_user_count(),
        "active_sessions": get_active_sessions_count(),
        "features": [
            "✅ Local Redis storage",
            "✅ Google OAuth",
            "✅ JWT + Session tokens",
            "✅ Real-time session management",
            "✅ CORS enabled"
        ],
        "environment": ENVIRONMENT
    }

@app.get("/api/auth/google")
async def google_login():
    """Get Google OAuth URL"""
    redirect_uri = "http://localhost:8000/api/auth/google/callback"
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid email profile&"
        f"access_type=offline"
    )
    return {"auth_url": google_auth_url}

@app.get("/api/auth/google/callback")
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code provided")
        
        redirect_uri = "http://localhost:8000/api/auth/google/callback"
        
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            )
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Get user info
            user_response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            user_response.raise_for_status()
            google_user = user_response.json()
        
        # Find or create user
        user = RedisUser.find_by_email(google_user["email"])
        if not user:
            user = RedisUser(
                email=google_user["email"],
                name=google_user["name"],
                avatar=google_user.get("picture", ""),
                role="volunteer",
                auth_provider="google",
                provider_id=google_user.get("sub")
            )
            user.save()
        else:
            # Update user info
            user.name = google_user["name"]
            user.avatar = google_user.get("picture", user.avatar)
            if not user.provider_id:
                user.provider_id = google_user.get("sub")
            user.save()
        
        # Create auth response
        auth_data = create_auth_response(user, request)
        
        # Redirect to frontend
        frontend_url = f"http://localhost:5173/auth/callback?token={auth_data['access_token']}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        error_url = f"http://localhost:5173/auth/error?message=Authentication failed"
        return RedirectResponse(url=error_url)

@app.post("/api/auth/signup")
async def signup(request: Request):
    """Manual signup"""
    try:
        data = await request.json()
        
        # Check if user exists
        existing_user = RedisUser.find_by_email(data["email"])
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = RedisUser(
            email=data["email"],
            name=data["name"],
            role=data.get("role", "volunteer"),
            organization_name=data.get("organizationName"),
            auth_provider="local"
        )
        user.save()
        
        # Create auth response
        auth_data = create_auth_response(user, request)
        
        return auth_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed")

@app.post("/api/auth/login")
async def login(request: Request):
    """Manual login"""
    try:
        data = await request.json()
        
        user = RedisUser.find_by_email(data["email"])
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Create auth response
        auth_data = create_auth_response(user, request)
        
        return auth_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: RedisUser = Depends(get_current_user)):
    """Get current user info"""
    return {"user": current_user.to_dict()}

@app.post("/api/auth/logout")
async def logout(request: Request):
    """Logout user"""
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # Try to find and revoke session
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            session_token = payload.get("session_token")
            if session_token:
                session = RedisSession.find_by_token(session_token)
                if session:
                    session.revoke()
            
            return {"message": "Logged out successfully", "success": True}
        else:
            return {"message": "No token provided", "success": False}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Logout completed", "success": True}

@app.get("/api/auth/health")
async def health_check():
    """Health check for Redis and API"""
    redis_status = test_redis_connection()
    
    return {
        "status": "healthy" if redis_status else "degraded",
        "redis": "connected" if redis_status else "disconnected",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": ENVIRONMENT
    }

@app.get("/stats")
async def get_stats():
    """Get system stats"""
    try:
        all_users = RedisUser.get_all_users()
        volunteers = sum(1 for user in all_users if user.role == "volunteer")
        organizers = sum(1 for user in all_users if user.role == "organizer")
        
        return {
            "users": {
                "total": len(all_users),
                "volunteers": volunteers,
                "organizers": organizers
            },
            "sessions": {
                "active": get_active_sessions_count()
            },
            "redis": {
                "connected": test_redis_connection(),
                "url": REDIS_URL
            },
            "top_users": [
                {"name": user.name, "points": user.points, "level": user.level}
                for user in sorted(all_users, key=lambda x: x.points, reverse=True)[:5]
            ]
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": "Could not fetch stats"}

if __name__ == "__main__":
    import uvicorn
    
    # Validate configuration
    print("🔧 Validating configuration...")
    if validate_config():
        print("✅ Configuration valid")
    else:
        print("❌ Configuration issues detected")
    
    print("🚀 Starting WaveAI with Local Redis...")
    print(f"📊 Environment: {ENVIRONMENT}")
    print(f"🔗 Redis URL: {REDIS_URL}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)