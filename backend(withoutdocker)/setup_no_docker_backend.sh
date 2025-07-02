#!/bin/bash

echo "🌿 Setting up WaveAI Backend - No Docker Branch"

# Check current directory
if [ ! -d "backend" ]; then
    echo "❌ Please run this from your project root (where backend folder exists)"
    exit 1
fi

cd backend

# Create branch if not exists
echo "🌿 Creating/switching to backend-no-docker branch..."
git checkout -b backend-no-docker 2>/dev/null || git checkout backend-no-docker

echo "📁 Setting up no-docker files..."

# Copy requirements
cat > requirements-no-docker.txt << 'EOF'
# FastAPI Core (stable versions)
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Redis client (for local Redis)
redis==5.0.1
hiredis==2.2.3

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# OAuth
httpx==0.25.2

# Environment variables
python-dotenv==1.0.0

# CORS
pydantic==2.4.2
EOF

# Copy environment file
cat > .env-no-docker << 'EOF'
# Redis (local installation)
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT Configuration
SECRET_KEY=your-super-secret-key-for-jwt-tokens-min-32-chars-hackathon
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id-from-console
GOOGLE_CLIENT_SECRET=your-google-client-secret

# CORS Origins
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Environment
ENVIRONMENT=development
DEBUG=true
EOF

# Make setup script executable
chmod +x setup_local_redis.sh

echo "✅ Files created!"
echo ""
echo "🚀 Quick Setup Commands:"
echo ""
echo "1. Install local Redis:"
echo "   ./setup_local_redis.sh"
echo ""
echo "2. Install Python dependencies:"
echo "   pip install -r requirements-no-docker.txt"
echo ""
echo "3. Copy environment file:"
echo "   cp .env-no-docker .env"
echo ""
echo "4. Update Google OAuth credentials in .env file"
echo ""
echo "5. Run the API:"
echo "   python main_no_docker.py"
echo ""
echo "📚 API will be available at:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs" 
echo "   - Stats: http://localhost:8000/stats"
echo ""
echo "🧪 Test commands:"
echo "   curl http://localhost:8000/"
echo "   curl http://localhost:8000/api/auth/health"