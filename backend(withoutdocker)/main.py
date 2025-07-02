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
        "environment": ENVIRONMENT,
        "google_oauth_configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
    }

@app.get("/api/auth/google")
async def google_login():
    """Get Google OAuth URL"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file"
        )
    
    redirect_uri = "http://localhost:8000/api/auth/google/callback"
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid email profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    logger.info(f"Generated Google Auth URL for client ID: {GOOGLE_CLIENT_ID[:10]}...")
    return {"auth_url": google_auth_url}

@app.get("/api/auth/google/callback")
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        code = request.query_params.get("code")
        error = request.query_params.get("error")
        
        if error:
            logger.error(f"Google OAuth error: {error}")
            error_url = f"http://localhost:5173/auth/callback?error={error}&message=Google OAuth failed"
            return RedirectResponse(url=error_url)
        
        if not code:
            logger.error("No authorization code provided")
            error_url = f"http://localhost:5173/auth/callback?error=no_code&message=No authorization code provided"
            return RedirectResponse(url=error_url)
        
        redirect_uri = "http://localhost:8000/api/auth/google/callback"
        
        logger.info(f"Exchanging code for tokens...")
        
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
            
            if token_response.status_code != 200:
                logger.error(f"Token exchange failed: {token_response.status_code} - {token_response.text}")
                error_url = f"http://localhost:5173/auth/callback?error=token_exchange&message=Failed to exchange code for token"
                return RedirectResponse(url=error_url)
            
            tokens = token_response.json()
            
            # Get user info
            user_response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            
            if user_response.status_code != 200:
                logger.error(f"User info fetch failed: {user_response.status_code} - {user_response.text}")
                error_url = f"http://localhost:5173/auth/callback?error=user_info&message=Failed to get user information"
                return RedirectResponse(url=error_url)
            
            google_user = user_response.json()
            logger.info(f"Got user info for: {google_user.get('email')}")
        
        # Find or create user
        user = RedisUser.find_by_email(google_user["email"])
        if not user:
            logger.info(f"Creating new user for: {google_user['email']}")
            user = RedisUser(
                email=google_user["email"],
                name=google_user["name"],
                avatar=google_user.get("picture", ""),
                role="volunteer",  # Default role
                auth_provider="google",
                provider_id=google_user.get("sub")
            )
            user.save()
        else:
            logger.info(f"Updating existing user: {google_user['email']}")
            # Update user info
            user.name = google_user["name"]
            user.avatar = google_user.get("picture", user.avatar)
            if not user.provider_id:
                user.provider_id = google_user.get("sub")
            user.save()
        
        # Create auth response
        auth_data = create_auth_response(user, request)
        
        # Redirect to frontend with token
        frontend_url = f"http://localhost:5173/auth/callback?token={auth_data['access_token']}"
        logger.info(f"Redirecting to frontend: {frontend_url[:50]}...")
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        error_url = f"http://localhost:5173/auth/callback?error=server_error&message=Authentication failed"
        return RedirectResponse(url=error_url)

@app.post("/api/auth/signup")
async def signup(request: Request):
    """Manual signup"""
    try:
        data = await request.json()
        logger.info(f"Signup attempt for email: {data.get('email')}")
        
        # Check if user exists
        existing_user = RedisUser.find_by_email(data["email"])
        if existing_user:
            logger.warning(f"User already exists: {data['email']}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = RedisUser(
            email=data["email"],
            name=data["name"],
            role=data.get("role", "volunteer"),
            organization_name=data.get("organizationName"),
            auth_provider="local"
        )
        
        if user.save():
            logger.info(f"User created successfully: {data['email']}")
        else:
            logger.error(f"Failed to save user: {data['email']}")
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create auth response
        auth_data = create_auth_response(user, request)
        
        return auth_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Signup failed")

@app.post("/api/auth/login")
async def login(request: Request):
    """Manual login"""
    try:
        data = await request.json()
        logger.info(f"Login attempt for email: {data.get('email')}")
        
        user = RedisUser.find_by_email(data["email"])
        if not user:
            logger.warning(f"User not found: {data['email']}")
            raise HTTPException(status_code=400, detail="User not found")
        
        logger.info(f"User found, creating auth response for: {data['email']}")
        
        # Create auth response
        auth_data = create_auth_response(user, request)
        
        return auth_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
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
        logger.error(f"Logout error: {str(e)}")
        return {"message": "Logout completed", "success": True}

@app.get("/api/auth/health")
async def health_check():
    """Health check for Redis and API"""
    redis_status = test_redis_connection()
    
    return {
        "status": "healthy" if redis_status else "degraded",
        "redis": "connected" if redis_status else "disconnected",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": ENVIRONMENT,
        "google_oauth": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
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
        logger.error(f"Stats error: {str(e)}")
        return {"error": "Could not fetch stats"}

# Debug endpoints
@app.get("/debug/redis")
async def debug_redis():
    """Debug Redis contents"""
    try:
        from redis_models_no_docker import redis_client
        if not redis_client:
            return {"error": "Redis not connected"}
        
        # Get all keys
        all_keys = redis_client.keys("*")
        
        result = {
            "total_keys": len(all_keys),
            "keys": all_keys,
            "users": {},
            "sessions": {}
        }
        
        # Get user data
        for key in all_keys:
            if key.startswith("user:") and not key.startswith("user_by_id:"):
                user_data = redis_client.hgetall(key)
                result["users"][key] = user_data
            elif key.startswith("session:") and not key.startswith("session_by_id:"):
                session_data = redis_client.hgetall(key)
                result["sessions"][key] = session_data
        
        return result
    except Exception as e:
        return {"error": str(e)}

@app.delete("/debug/redis/clear")
async def clear_redis():
    """Clear all Redis data - USE WITH CAUTION"""
    try:
        from redis_models_no_docker import redis_client
        if not redis_client:
            return {"error": "Redis not connected"}
        
        keys_before = len(redis_client.keys("*"))
        redis_client.flushall()
        keys_after = len(redis_client.keys("*"))
        
        return {
            "message": "All Redis data cleared successfully",
            "keys_cleared": keys_before,
            "keys_remaining": keys_after
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/config")
async def debug_config():
    """Check configuration"""
    return {
        "google_client_id_set": bool(GOOGLE_CLIENT_ID),
        "google_client_secret_set": bool(GOOGLE_CLIENT_SECRET),
        "google_client_id_preview": GOOGLE_CLIENT_ID[:10] + "..." if GOOGLE_CLIENT_ID else "NOT SET",
        "redis_url": REDIS_URL,
        "cors_origins": CORS_ORIGINS,
        "environment": ENVIRONMENT,
        "secret_key_set": bool(SECRET_KEY),
        "access_token_expire_hours": ACCESS_TOKEN_EXPIRE_HOURS
    }

@app.get("/debug/test-user-creation")
async def test_user_creation():
    """Test creating a user manually"""
    try:
        test_email = f"test-{datetime.utcnow().timestamp()}@example.com"
        
        user = RedisUser(
            email=test_email,
            name="Test User",
            role="volunteer",
            auth_provider="manual_test"
        )
        
        saved = user.save()
        
        # Try to retrieve the user
        retrieved_user = RedisUser.find_by_email(test_email)
        
        return {
            "test_email": test_email,
            "save_successful": saved,
            "user_retrieved": retrieved_user is not None,
            "user_data": retrieved_user.to_dict() if retrieved_user else None
        }
    except Exception as e:
        return {"error": str(e), "test_failed": True}

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
    print(f"🔑 Google OAuth: {'✅ Configured' if GOOGLE_CLIENT_ID else '❌ Not configured'}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)