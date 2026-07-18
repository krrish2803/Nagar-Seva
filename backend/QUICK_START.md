# NagarSeva Backend - Quick Start Guide

## Overview

This guide will help you get the NagarSeva FastAPI backend running locally in minutes.

## Prerequisites

- **Python 3.9+**
- **Docker & Docker Compose** (optional, recommended for MongoDB and Redis)
- **Git**
- **At least 2GB free disk space**

## Quick Start (Option 1: Docker - Recommended)

### 1. Clone the Repository
```bash
cd backend
```

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Start Services with Docker
```bash
docker-compose -f docker-compose-dev.yml up -d
```

### 4. Access the API
- **API Docs**: http://localhost:8000/docs
- **Redis Commander**: http://localhost:8081
- **Mongo Express**: http://localhost:8082

### 5. Stop Services
```bash
docker-compose -f docker-compose-dev.yml down
```

---

## Quick Start (Option 2: Automated Startup Script)

### 1. Make Script Executable
```bash
chmod +x startup.sh
```

### 2. Run Startup Script
```bash
./startup.sh
```

This script will:
- ✓ Check Python installation
- ✓ Create virtual environment
- ✓ Install dependencies
- ✓ Start Docker containers (if available)
- ✓ Start FastAPI server

### 3. Access the API
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Quick Start (Option 3: Manual Setup)

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start MongoDB Locally
```bash
# Using Docker (recommended)
docker run -d -p 27017:27017 --name nagarseva_mongo mongo:7.0-alpine

# Or if MongoDB is installed locally
mongod --dbpath /path/to/data
```

### 4. Start Redis Locally
```bash
# Using Docker (recommended)
docker run -d -p 6379:6379 --name nagarseva_redis redis:7-alpine

# Or if Redis is installed locally
redis-server
```

### 5. Configure Environment
```bash
cp .env.example .env
```

### 6. Start FastAPI Server
```bash
cd app
uvicorn main:app --reload --port 8000
```

---

## API Endpoints Overview

### Authentication
```bash
# Login
POST /api/auth/login
{
  "username": "citizen_demo@example.com",
  "password": "demo123"
}

# Demo credentials:
# - Citizen: citizen_demo@example.com / demo123
# - Official: official_demo@example.com / demo123
```

### Complaints
```bash
# Submit complaint (with file uploads)
POST /api/complaints/report

# List complaints
GET /api/complaints?status=submitted&ward_id=W001&skip=0&limit=10

# Get complaint details
GET /api/complaints/{complaint_id}

# Update complaint status
PUT /api/complaints/{complaint_id}/status
```

### Heatmap & Analytics
```bash
# Get safety heatmap data
GET /api/heatmap/data?time_period_days=30&min_severity=medium

# Get analytics report
GET /api/heatmap/analytics?period_days=30
```

### Routes
```bash
# Calculate safer route
POST /api/routes/safer-path
{
  "origin_latitude": 40.7128,
  "origin_longitude": -74.0060,
  "destination_latitude": 40.7200,
  "destination_longitude": -74.0100,
  "route_type": "safest"
}
```

### Escalation
```bash
# Get escalation queue
GET /api/escalation/queue?status=pending

# Create escalation
POST /api/escalation/create
{
  "complaint_id": "COMP_123",
  "escalation_reason": "SLA exceeded",
  "escalated_by_official_id": "OFF_001"
}
```

### Health Check
```bash
GET /health
GET /info
GET /
```

---

## Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_classification_agent.py -v
```

### Run Specific Test
```bash
pytest tests/test_classification_agent.py::TestClassificationAgent::test_determine_severity_critical -v
```

---

## Environment Configuration

Key environment variables in `.env`:

```env
# Server
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=nagarseva_db

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8000

# File Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=10

# NVIDIA NIM (optional)
NVIDIA_API_KEY=your-api-key
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1
```

---

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/new-agent
```

### 2. Make Changes
- Edit files in `app/` directory
- Changes are automatically reloaded (with `--reload`)

### 3. Write Tests
```bash
# Create test in tests/ directory
# Run tests
pytest tests/test_new_feature.py -v
```

### 4. Check Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### 5. Commit and Push
```bash
git add .
git commit -m "feat: description of changes"
git push origin feature/new-agent
```

---

## Troubleshooting

### MongoDB Connection Error
```
Error: connect ECONNREFUSED 127.0.0.1:27017

Solution:
1. Ensure MongoDB is running: docker-compose -f docker-compose-dev.yml up -d
2. Or start MongoDB locally: mongod
```

### Redis Connection Error
```
Error: Error -1 connecting to localhost:6379

Solution:
1. Ensure Redis is running: docker-compose -f docker-compose-dev.yml up -d
2. Or start Redis locally: redis-server
```

### Port Already in Use
```
Error: Address already in use: ('0.0.0.0', 8000)

Solution:
1. Stop existing process: lsof -ti:8000 | xargs kill -9
2. Or use different port: uvicorn app.main:app --port 8001
```

### Module Import Errors
```
Error: ModuleNotFoundError: No module named 'app'

Solution:
1. Ensure you're in the correct directory
2. Check PYTHONPATH: export PYTHONPATH="${PYTHONPATH}:$(pwd)"
3. Reinstall dependencies: pip install -r requirements.txt
```

### Celery Worker Issues
```
Error: Failed to connect to Redis

Solution:
1. Ensure Redis is running
2. Check CELERY_BROKER_URL in .env
3. Restart Celery worker
```

---

## Project Structure

```
backend/
├── app/
│   ├── agents/                 # LLM agents (classification, routing, etc.)
│   ├── models/                 # MongoDB Pydantic models
│   ├── routers/                # API route handlers
│   ├── schemas/                # Request/response schemas
│   ├── tasks/                  # Celery async tasks
│   ├── utils/                  # Helper utilities
│   ├── config.py               # Configuration settings
│   ├── main.py                 # FastAPI app entry point
│   └── __init__.py
├── tests/                      # Unit and integration tests
├── uploads/                    # File storage (created automatically)
├── Dockerfile                  # Docker image definition
├── docker-compose-dev.yml      # Local development services
├── docker-compose.yml          # Production services
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── startup.sh                  # Development startup script
├── Makefile                    # Build commands
├── README.md                   # Full documentation
├── QUICK_START.md              # This file
└── ...
```

---

## File Upload

### Supported Types
- Images: `.jpg`, `.jpeg`, `.png`, `.gif`
- Audio: `.wav`, `.mp3`, `.m4a`
- Max size: 10MB (configurable)

### Upload Directory
- Files stored in: `backend/uploads/`
- Format: `complaint_{id}_{type}.{ext}`

---

## API Response Format

### Success Response (200 OK)
```json
{
  "complaint_id": "COMP_uuid",
  "status": "assigned",
  "issue_type": "pothole",
  "severity": "high",
  "assigned_to_official_id": "OFF_123",
  "sla_days": 7,
  "message": "Complaint successfully submitted"
}
```

### Error Response (4xx/5xx)
```json
{
  "error": "Invalid input",
  "detail": "Latitude must be between -90 and 90",
  "status_code": 400
}
```

---

## Next Steps

1. **Review API Documentation**: http://localhost:8000/docs
2. **Check Examples**: See `EXAMPLES.md`
3. **Run Tests**: `pytest tests/ -v`
4. **Explore Code**: Start with `app/main.py`
5. **Integrate Frontend**: Connect to http://localhost:8000

---

## Useful Commands

```bash
# View logs
docker-compose -f docker-compose-dev.yml logs -f backend

# Access MongoDB shell
docker-compose -f docker-compose-dev.yml exec mongodb mongosh

# View Redis data
docker-compose -f docker-compose-dev.yml exec redis redis-cli

# Rebuild Docker images
docker-compose -f docker-compose-dev.yml build --no-cache

# Clean up all containers
docker-compose -f docker-compose-dev.yml down -v

# Format Python code
black app/

# Run type checking
mypy app/

# Generate API schema
curl http://localhost:8000/openapi.json > openapi.json
```

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **README**: See `README.md`
- **Examples**: See `EXAMPLES.md`
- **Project Summary**: See `PROJECT_SUMMARY.md`

---

## License

This project is part of NagarSeva - Civic Issue Management Platform.

---

**Last Updated**: January 2024
**Backend Version**: 0.1.0
