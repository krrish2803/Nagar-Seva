#!/bin/bash

# NagarSeva Backend - Quick Setup Script
# Usage: bash setup.sh

set -e

echo "🚀 NagarSeva Backend Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $python_version"

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate
echo "  Virtual environment activated"

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "  pip upgraded"

# Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "  Dependencies installed"

# Create .env file
echo ""
echo "✓ Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  .env file created (copy of .env.example)"
    echo "  Please edit .env with your configuration"
else
    echo "  .env already exists"
fi

# Create uploads directory
echo ""
echo "✓ Creating uploads directory..."
mkdir -p uploads
echo "  uploads/ directory ready"

# Check Docker availability
echo ""
echo "✓ Checking Docker availability..."
if command -v docker &> /dev/null; then
    echo "  Docker found: $(docker --version)"
    if command -v docker-compose &> /dev/null; then
        echo "  Docker Compose found: $(docker-compose --version)"
        docker_available=true
    else
        echo "  ⚠ Docker Compose not found (optional)"
        docker_available=false
    fi
else
    echo "  ⚠ Docker not found (optional - needed for local MongoDB/Redis)"
    docker_available=false
fi

# Display setup summary
echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Configure your environment:"
echo "   nano .env"
echo ""
echo "2. Start MongoDB and Redis:"
if [ "$docker_available" = true ]; then
    echo "   docker-compose up -d mongodb redis"
else
    echo "   # Install Docker, or start MongoDB/Redis manually"
fi
echo ""
echo "3. Start the FastAPI server:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Optional: Start Celery worker (in another terminal):"
echo "   celery -A app.tasks.celery_tasks worker --loglevel=info"
echo ""
echo "5. Optional: Start Celery beat scheduler:"
echo "   celery -A app.tasks.celery_tasks beat --loglevel=info"
echo ""
echo "6. Access the API:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Full documentation"
echo "   - EXAMPLES.md - API usage examples"
echo "   - PROJECT_SUMMARY.md - Project overview"
echo ""
echo "To activate virtual environment in future sessions:"
echo "   source venv/bin/activate"
echo ""
