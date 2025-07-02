from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from datetime import datetime
import uuid
import logging
from fastapi import Depends
from models import User, get_user_by_email
from oauth import get_google_user
from auth_utils import create_auth_response, get_current_user, logout_user
from config import GOOGLE_CLIENT_ID

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth")

@router.get("/google")
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

@router.get("/google/callback")
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code provided")
        
        redirect_uri = "http://localhost:8000/api/auth/google/callback"
        google_user = await get_google_user(code, redirect_uri)
        
        # Find or create user
        user = get_user_by_email(google_user["email"])
        if not user:
            user = User(
                email=google_user["email"],
                name=google_user["name"],
                avatar=google_user.get("picture", ""),
                role="volunteer",  # Default role
                auth_provider="google",
                provider_id=google_user.get("sub")
            )
            user.save()
        else:
            # Update user info from Google
            user.name = google_user["name"]
            user.avatar = google_user.get("picture", user.avatar)
            if not user.provider_id:
                user.provider_id = google_user.get("sub")
            user.save()
        
        # Create auth tokens
        auth_data = create_auth_response(user, request)
        
        # Redirect to frontend with token
        frontend_url = f"http://localhost:5173/auth/callback?token={auth_data['access_token']}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        error_url = f"http://localhost:5173/auth/error?message=Authentication failed"
        return RedirectResponse(url=error_url)

@router.post("/signup")
async def signup(request: Request):
    """Manual signup"""
    try:
        data = await request.json()
        
        # Check if user exists
        existing_user = get_user_by_email(data["email"])
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = User(
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

@router.post("/login")
async def login(request: Request):
    """Manual login (simplified for hackathon)"""
    try:
        data = await request.json()
        
        user = get_user_by_email(data["email"])
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

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {"user": current_user.to_dict()}

@router.post("/logout")
async def logout(request: Request):
    """Logout user"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            success = logout_user(token)
            return {"message": "Logged out successfully", "success": success}
        else:
            return {"message": "No token provided", "success": False}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Logout failed", "success": False}

@router.get("/sessions")
async def get_user_sessions(current_user: User = Depends(get_current_user)):
    """Get all active sessions for current user (useful for hackathon debugging)"""
    from models import Session
    try:
        sessions = Session.find(
            Session.user_id == current_user.id, 
            Session.is_active == True
        ).all()
        
        session_data = []
        for session in sessions:
            session_data.append({
                "id": session.id,
                "created_at": session.created_at,
                "expires_at": session.expires_at,
                "user_agent": session.user_agent,
                "ip_address": session.ip_address
            })
        
        return {"sessions": session_data}
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        return {"sessions": []}

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for Redis connection"""
    try:
        from models import redis
        redis.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": "disconnected", "error": str(e)}