from redis_om import get_redis_connection, HashModel, Field
from typing import Optional
from datetime import datetime
import uuid
from config import REDIS_URL

# Redis connection
redis = get_redis_connection(url=REDIS_URL, decode_responses=True)

class User(HashModel):
    """User model stored in Redis"""
    class Meta:
        database = redis
    
    # Basic info
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(index=True)
    name: str
    avatar: Optional[str] = None
    role: str = Field(default="volunteer")  # volunteer or organizer
    
    # Volunteer stats
    points: int = Field(default=0)
    level: str = Field(default="Newcomer")
    badges: int = Field(default=0)
    
    # Organizer stats
    organization_name: Optional[str] = None
    events_organized: int = Field(default=0)
    total_volunteers: int = Field(default=0)
    is_verified: bool = Field(default=False)
    
    # Meta
    is_active: bool = Field(default=True)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_login: Optional[str] = None
    
    # OAuth
    auth_provider: str = Field(default="local")  # local, google, github
    provider_id: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar": self.avatar,
            "role": self.role,
            "points": self.points,
            "level": self.level,
            "badges": self.badges,
            "organizationName": self.organization_name,
            "eventsOrganized": self.events_organized,
            "totalVolunteers": self.total_volunteers,
            "isVerified": self.is_verified,
            "joinedAt": self.created_at,
            "lastLogin": self.last_login,
            "authProvider": self.auth_provider
        }

class Session(HashModel):
    """Session model for managing user sessions"""
    class Meta:
        database = redis
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    token: str = Field(index=True)
    expires_at: str
    is_active: bool = Field(default=True)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

# Helper functions for Redis operations
def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email"""
    try:
        users = User.find(User.email == email).all()
        return users[0] if users else None
    except:
        return None

def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID"""
    try:
        return User.get(user_id)
    except:
        return None

def create_user_session(user_id: str, token: str, expires_at: str, user_agent: str = None, ip_address: str = None) -> Session:
    """Create a new session"""
    session = Session(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address
    )
    session.save()
    return session

def get_session_by_token(token: str) -> Optional[Session]:
    """Get session by token"""
    try:
        sessions = Session.find(Session.token == token, Session.is_active == True).all()
        return sessions[0] if sessions else None
    except:
        return None

def revoke_session(token: str) -> bool:
    """Revoke a session"""
    try:
        session = get_session_by_token(token)
        if session:
            session.is_active = False
            session.save()
            return True
        return False
    except:
        return False

def revoke_all_user_sessions(user_id: str) -> bool:
    """Revoke all sessions for a user"""
    try:
        sessions = Session.find(Session.user_id == user_id, Session.is_active == True).all()
        for session in sessions:
            session.is_active = False
            session.save()
        return True
    except:
        return False

# Simple cache functions for additional data
def cache_set(key: str, value: str, expire_seconds: int = 3600):
    """Set cache value with expiration"""
    redis.setex(key, expire_seconds, value)

def cache_get(key: str) -> Optional[str]:
    """Get cache value"""
    return redis.get(key)

def cache_delete(key: str):
    """Delete cache value"""
    redis.delete(key)