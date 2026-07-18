#!/bin/bash

# NagarSeva Backend - Local Development Startup Script
# This script sets up the complete development environment

set -e  # Exit on error

echo "================================"
echo "NagarSeva Backend - Dev Setup"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}[1/6] Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
echo ""

# Create uploads directory
echo -e "${BLUE}[2/6] Creating uploads directory...${NC}"
if [ ! -d "uploads" ]; then
    mkdir -p uploads
    echo -e "${GREEN}✓ Created uploads/ directory${NC}"
else
    echo -e "${GREEN}✓ uploads/ directory already exists${NC}"
fi
echo ""

# Install Python dependencies
echo -e "${BLUE}[3/6] Installing Python dependencies...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Created virtual environment${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ Upgraded pip${NC}"

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Installed Python dependencies${NC}"
else
    echo -e "${YELLOW}⚠ requirements.txt not found${NC}"
fi
echo ""

# Check Docker
echo -e "${BLUE}[4/6] Checking Docker setup...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker is not installed (optional for local MongoDB/Redis)${NC}"
    echo -e "${YELLOW}  You can either:${NC}"
    echo -e "${YELLOW}  1. Install Docker and use docker-compose${NC}"
    echo -e "${YELLOW}  2. Run MongoDB and Redis locally${NC}"
else
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓ $DOCKER_VERSION found${NC}"
    
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_VERSION=$(docker-compose --version)
        echo -e "${GREEN}✓ $DOCKER_COMPOSE_VERSION found${NC}"
        
        echo ""
        echo -e "${BLUE}Starting Docker containers...${NC}"
        docker-compose -f docker-compose-dev.yml up -d
        echo -e "${GREEN}✓ Docker containers started${NC}"
        echo ""
        echo -e "${YELLOW}Container URLs:${NC}"
        echo -e "  - FastAPI Docs: http://localhost:8000/docs"
        echo -e "  - Redis Commander: http://localhost:8081"
        echo -e "  - Mongo Express: http://localhost:8082"
        
        # Wait for services to be ready
        echo ""
        echo -e "${BLUE}Waiting for services to be ready...${NC}"
        sleep 5
        echo -e "${GREEN}✓ Services should be ready${NC}"
    else
        echo -e "${YELLOW}⚠ docker-compose is not installed${NC}"
    fi
fi
echo ""

# Create .env file if it doesn't exist
echo -e "${BLUE}[5/6] Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
    else
        echo -e "${YELLOW}⚠ .env.example not found${NC}"
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Start the FastAPI server
echo -e "${BLUE}[6/6] Starting FastAPI development server...${NC}"
echo -e "${YELLOW}API Documentation: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}OpenAPI Schema: http://localhost:8000/openapi.json${NC}"
echo -e "${YELLOW}Health Check: http://localhost:8000/health${NC}"
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}NagarSeva Backend is starting...${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Run the application
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
