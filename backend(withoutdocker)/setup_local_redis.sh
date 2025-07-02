#!/bin/bash

echo "🚀 Setting up Local Redis for WaveAI (No Docker)"

# Detect OS and install Redis
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "📦 Installing Redis with Homebrew..."
    brew install redis
    
    echo "🔧 Starting Redis service..."
    brew services start redis
    
    echo "✅ Redis installed and started!"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
    
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        echo "📦 Installing Redis with apt..."
        sudo apt-get update
        sudo apt-get install -y redis-server
        
        echo "🔧 Starting Redis service..."
        sudo systemctl start redis
        sudo systemctl enable redis
        
    # Arch Linux
    elif command -v pacman &> /dev/null; then
        echo "📦 Installing Redis with pacman..."
        sudo pacman -S redis
        
        echo "🔧 Starting Redis service..."
        sudo systemctl start redis
        sudo systemctl enable redis
    else
        echo "❌ Unsupported Linux distribution"
        exit 1
    fi
    
    echo "✅ Redis installed and started!"
    
else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "Please install Redis manually and run: redis-server"
    exit 1
fi

# Test Redis connection
echo "🧪 Testing Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping | grep -q "PONG"; then
        echo "✅ Redis is running and responding!"
    else
        echo "❌ Redis is installed but not responding"
        echo "Try running: redis-server"
        exit 1
    fi
else
    echo "❌ redis-cli not found"
    exit 1
fi

echo ""
echo "🎯 Redis Setup Complete!"
echo "🔗 Redis URL: redis://localhost:6379"
echo "🧪 Test command: redis-cli ping"
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements-no-docker.txt"
echo "2. Copy .env-no-docker to .env: cp .env-no-docker .env"
echo "3. Update your Google OAuth credentials in .env"
echo "4. Run the API: python main_no_docker.py"sudo systemctl start redis-server
        sudo systemctl enable redis-server
    
    # CentOS/RHEL/Fedora
    elif command -v yum &> /dev/null; then
        echo "📦 Installing Redis with yum..."
        sudo yum install -y redis
        
        echo "🔧 Starting Redis service..."