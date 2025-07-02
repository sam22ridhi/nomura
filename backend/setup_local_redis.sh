#!/bin/bash

echo "🚀 Starting WaveAI with Redis for Hackathon..."

# Start Redis
echo "📦 Starting Redis..."
docker-compose up -d

# Wait for Redis
echo "⏳ Waiting for Redis to be ready..."
sleep 3

# Test Redis connection
echo "🔍 Testing Redis connection..."
docker exec waveai_redis redis-cli ping

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Start backend
echo "🔧 Starting backend..."
python main.py &
BACKEND_PID=$!

echo "✅ WaveAI with Redis is running!"
echo ""
echo "🔗 Frontend: http://localhost:5173"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 API Docs: http://localhost:8000/docs"
echo "📊 Redis UI: http://localhost:8081"
echo "📈 Stats: http://localhost:8000/stats"
echo ""
echo "🧪 Quick Tests:"
echo "curl http://localhost:8000/"
echo "curl http://localhost:8000/api/auth/health"
echo "curl http://localhost:8000/stats"
echo ""

# Wait for user input to stop
read -p "Press Enter to stop all services..."

# Clean shutdown
echo "🛑 Stopping services..."
kill $BACKEND_PID 2>/dev/null
docker-compose down

echo "✅ All services stopped."venv