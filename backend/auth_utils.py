from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS
from models import User, Session, get_user_by_id, get_session_by_token, create_user_session
import secrets
import logging

logger = logging.getLogger(__name__)

# OAuth2 scheme
security = HTTPBearer()

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
    # Generate secure random token
    token = secrets.token_urlsafe(64)
    expires_at = (datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).isoformat()
    
    # Get request info
    user_agent = request.headers.get("user-agent") if request else None
    ip_address = request.client.host if request else None
    
    # Store session in Redis
    create_user_session(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address
    )
    
    return token

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_from_session_token(token: str) -> Optional[User]:
    """Get user from session token stored in Redis"""
    try:
        session = get_session_by_token(token)
        if not session:
            return None
        
        # Check if session is expired
        expires_at = datetime.fromisoformat(session.expires_at)
        if datetime.utcnow() > expires_at:
            session.is_active = False
            session.save()
            return None
        
        # Get user
        user = get_user_by_id(session.user_id)
        return user
    except Exception as e:
        logger.error(f"Error getting user from session: {e}")
        return None

def get_user_from_jwt_token(token: str) -> Optional[User]:
    """Get user from JWT token"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    user_id = payload.get("user_id")
    if user_id is None:
        return None
    
    user = get_user_by_id(user_id)
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # Try JWT first (for OAuth compatibility)
        user = get_user_from_jwt_token(token)
        if user and user.is_active:
            return user
        
        # Try session token (for regular login)
        user = get_user_from_session_token(token)
        if user and user.is_active:
            return user
        
        raise credentials_exception
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def create_auth_response(user: User, request: Request = None) -> dict:
    """Create authentication response with both JWT and session token"""
    # Create JWT for OAuth compatibility
    jwt_token = create_access_token(data={
        "sub": user.email, 
        "user_id": user.id,
        "role": user.role
    })
    
    # Create session token for session management
    session_token = create_session_token(user.id, request)
    
    # Update last login
    user.last_login = datetime.utcnow().isoformat()
    user.save()
    
    return {
        "access_token": jwt_token,
        "session_token": session_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        "user": user.to_dict()
    }

def logout_user(token: str) -> bool:
    """Logout user by revoking session"""
    try:
        # Try to revoke session token
        session = get_session_by_token(token)
        if session:
            session.is_active = False
            session.save()
            return True
        return False
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return False