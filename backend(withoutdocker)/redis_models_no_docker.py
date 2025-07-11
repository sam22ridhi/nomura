import redis
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from config_no_docker import get_redis_url
import logging

logger = logging.getLogger(__name__)

# Redis connection
try:
    redis_client = redis.Redis.from_url(get_redis_url(), decode_responses=True)
    redis_client.ping()
    print("✅ Redis connected successfully")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    redis_client = None

class RedisUser:
    """Redis-based User model"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.email = kwargs.get('email')
        self.name = kwargs.get('name')
        self.avatar = kwargs.get('avatar', '')
        self.role = kwargs.get('role', 'volunteer')
        
        # Volunteer stats
        self.points = int(kwargs.get('points', 0))
        self.level = kwargs.get('level', 'Newcomer')
        self.badges = int(kwargs.get('badges', 0))
        
        # Organizer stats
        self.organization_name = kwargs.get('organization_name', '')
        self.events_organized = int(kwargs.get('events_organized', 0))
        self.total_volunteers = int(kwargs.get('total_volunteers', 0))
        self.is_verified = bool(kwargs.get('is_verified', False))
        
        # Meta
        self.is_active = bool(kwargs.get('is_active', True))
        self.created_at = kwargs.get('created_at', datetime.utcnow().isoformat())
        self.last_login = kwargs.get('last_login', '')
        
        # OAuth
        self.auth_provider = kwargs.get('auth_provider', 'local')
        self.provider_id = kwargs.get('provider_id', '')
    
    def save(self):
        """Save user to Redis"""
        if not redis_client:
            logger.error("Redis client not available")
            return False
        
        try:
            user_data = {
                'id': str(self.id),
                'email': str(self.email or ''),
                'name': str(self.name or ''),
                'avatar': str(self.avatar or ''),
                'role': str(self.role),
                'points': str(self.points),
                'level': str(self.level),
                'badges': str(self.badges),
                'organization_name': str(self.organization_name or ''),
                'events_organized': str(self.events_organized),
                'total_volunteers': str(self.total_volunteers),
                'is_verified': str(self.is_verified),
                'is_active': str(self.is_active),
                'created_at': str(self.created_at),
                'last_login': str(self.last_login or ''),
                'auth_provider': str(self.auth_provider),
                'provider_id': str(self.provider_id or '')
            }
            
            # Save with both email and ID as keys
            redis_client.hset(f"user:{self.email}", mapping=user_data)
            redis_client.hset(f"user_by_id:{self.id}", mapping=user_data)
            
            logger.info(f"User saved successfully: {self.email}")
            return True
        except Exception as e:
            logger.error(f"Error saving user {self.email}: {e}")
            return False
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'avatar': self.avatar,
            'role': self.role,
            'points': self.points,
            'level': self.level,
            'badges': self.badges,
            'organizationName': self.organization_name,
            'eventsOrganized': self.events_organized,
            'totalVolunteers': self.total_volunteers,
            'isVerified': self.is_verified,
            'isActive': self.is_active,
            'joinedAt': self.created_at,
            'lastLogin': self.last_login,
            'authProvider': self.auth_provider,
            'providerId': self.provider_id
        }
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['RedisUser']:
        """Find user by email"""
        if not redis_client:
            return None
        
        try:
            user_data = redis_client.hgetall(f"user:{email}")
            if user_data:
                # Convert string values back to appropriate types
                converted_data = {
                    'id': user_data.get('id'),
                    'email': user_data.get('email'),
                    'name': user_data.get('name'),
                    'avatar': user_data.get('avatar'),
                    'role': user_data.get('role'),
                    'points': int(user_data.get('points', 0)),
                    'level': user_data.get('level'),
                    'badges': int(user_data.get('badges', 0)),
                    'organization_name': user_data.get('organization_name'),
                    'events_organized': int(user_data.get('events_organized', 0)),
                    'total_volunteers': int(user_data.get('total_volunteers', 0)),
                    'is_verified': user_data.get('is_verified', 'False').lower() == 'true',
                    'is_active': user_data.get('is_active', 'True').lower() == 'true',
                    'created_at': user_data.get('created_at'),
                    'last_login': user_data.get('last_login'),
                    'auth_provider': user_data.get('auth_provider'),
                    'provider_id': user_data.get('provider_id')
                }
                return cls(**converted_data)
            return None
        except Exception as e:
            logger.error(f"Error finding user by email {email}: {e}")
            return None
    
    @classmethod
    def find_by_id(cls, user_id: str) -> Optional['RedisUser']:
        """Find user by ID"""
        if not redis_client:
            return None
        
        try:
            user_data = redis_client.hgetall(f"user_by_id:{user_id}")
            if user_data:
                # Convert string values back to appropriate types
                converted_data = {
                    'id': user_data.get('id'),
                    'email': user_data.get('email'),
                    'name': user_data.get('name'),
                    'avatar': user_data.get('avatar'),
                    'role': user_data.get('role'),
                    'points': int(user_data.get('points', 0)),
                    'level': user_data.get('level'),
                    'badges': int(user_data.get('badges', 0)),
                    'organization_name': user_data.get('organization_name'),
                    'events_organized': int(user_data.get('events_organized', 0)),
                    'total_volunteers': int(user_data.get('total_volunteers', 0)),
                    'is_verified': user_data.get('is_verified', 'False').lower() == 'true',
                    'is_active': user_data.get('is_active', 'True').lower() == 'true',
                    'created_at': user_data.get('created_at'),
                    'last_login': user_data.get('last_login'),
                    'auth_provider': user_data.get('auth_provider'),
                    'provider_id': user_data.get('provider_id')
                }
                return cls(**converted_data)
            return None
        except Exception as e:
            logger.error(f"Error finding user by ID {user_id}: {e}")
            return None
    
    @classmethod
    def get_all_users(cls) -> List['RedisUser']:
        """Get all users"""
        if not redis_client:
            return []
        
        try:
            user_keys = redis_client.keys("user:*")
            users = []
            for key in user_keys:
                if not key.startswith("user_by_id:"):
                    email = key.replace("user:", "")
                    user = cls.find_by_email(email)
                    if user:
                        users.append(user)
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

class RedisSession:
    """Redis-based Session model"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.user_id = kwargs.get('user_id')
        self.token = kwargs.get('token')
        self.expires_at = kwargs.get('expires_at')
        self.is_active = bool(kwargs.get('is_active', True))
        self.created_at = kwargs.get('created_at', datetime.utcnow().isoformat())
        self.user_agent = kwargs.get('user_agent', '')
        self.ip_address = kwargs.get('ip_address', '')
    
    def save(self):
        """Save session to Redis"""
        if not redis_client:
            return False
        
        try:
            session_data = {
                'id': str(self.id),
                'user_id': str(self.user_id),
                'token': str(self.token),
                'expires_at': str(self.expires_at),
                'is_active': str(self.is_active),
                'created_at': str(self.created_at),
                'user_agent': str(self.user_agent or ''),
                'ip_address': str(self.ip_address or '')
            }
            
            redis_client.hset(f"session:{self.token}", mapping=session_data)
            redis_client.hset(f"session_by_id:{self.id}", mapping=session_data)
            
            # Set expiration
            expire_seconds = 24 * 60 * 60  # 24 hours
            redis_client.expire(f"session:{self.token}", expire_seconds)
            redis_client.expire(f"session_by_id:{self.id}", expire_seconds)
            
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    @classmethod
    def find_by_token(cls, token: str) -> Optional['RedisSession']:
        """Find session by token"""
        if not redis_client:
            return None
        
        try:
            session_data = redis_client.hgetall(f"session:{token}")
            if session_data and session_data.get('is_active') == 'True':
                return cls(**session_data)
            return None
        except Exception as e:
            logger.error(f"Error finding session: {e}")
            return None
    
    def revoke(self):
        """Revoke session"""
        if not redis_client:
            return False
        
        try:
            self.is_active = False
            redis_client.hset(f"session:{self.token}", "is_active", "False")
            redis_client.hset(f"session_by_id:{self.id}", "is_active", "False")
            return True
        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            return False

# Helper functions
def get_user_count() -> int:
    """Get total user count"""
    if not redis_client:
        return 0
    
    try:
        user_keys = redis_client.keys("user:*")
        # Filter out user_by_id keys
        return len([key for key in user_keys if not key.startswith("user_by_id:")])
    except:
        return 0

def get_active_sessions_count() -> int:
    """Get active sessions count"""
    if not redis_client:
        return 0
    
    try:
        session_keys = redis_client.keys("session:*")
        active_count = 0
        for key in session_keys:
            if not key.startswith("session_by_id:"):
                session_data = redis_client.hgetall(key)
                if session_data.get('is_active') == 'True':
                    active_count += 1
        return active_count
    except:
        return 0

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    if not redis_client:
        return
    
    try:
        session_keys = redis_client.keys("session:*")
        for key in session_keys:
            if not key.startswith("session_by_id:"):
                session_data = redis_client.hgetall(key)
                if session_data.get('expires_at'):
                    expires_at = datetime.fromisoformat(session_data['expires_at'])
                    if datetime.utcnow() > expires_at:
                        redis_client.delete(key)
                        if session_data.get('id'):
                            redis_client.delete(f"session_by_id:{session_data['id']}")
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")

# Test Redis connection
def test_redis_connection():
    """Test Redis connection"""
    if not redis_client:
        return False
    
    try:
        redis_client.ping()
        return True
    except:
        return False