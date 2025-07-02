from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_routes import router as auth_router
from fastapi import Depends
from fastapi import Depends
from config import CORS_ORIGINS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="WaveAI API with Redis", 
    version="1.0.0",
    description="Hackathon-ready authentication with Redis"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth_router)

@app.get("/")
async def root():
    return {
        "message": "WaveAI API with Redis is running! 🌊", 
        "status": "healthy",
        "features": [
            "✅ Redis data storage",
            "✅ Google OAuth",
            "✅ JWT + Session tokens",
            "✅ Real-time session management",
            "✅ CORS enabled"
        ]
    }

@app.get("/stats")
async def get_stats():
    """Get system stats (useful for hackathon demos)"""
    try:
        from models import User, Session, redis
        
        # Count users
        total_users = len(User.find().all())
        volunteers = len(User.find(User.role == "volunteer").all())
        organizers = len(User.find(User.role == "organizer").all())
        
        # Count active sessions
        active_sessions = len(Session.find(Session.is_active == True).all())
        
        # Redis info
        redis_info = redis.info()
        
        return {
            "users": {
                "total": total_users,
                "volunteers": volunteers,
                "organizers": organizers
            },
            "sessions": {
                "active": active_sessions
            },
            "redis": {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory_human": redis_info.get("used_memory_human", "0B"),
                "uptime_in_seconds": redis_info.get("uptime_in_seconds", 0)
            }
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": "Could not fetch stats"}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting WaveAI with Redis...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)