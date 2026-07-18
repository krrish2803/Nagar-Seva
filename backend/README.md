# NagarSeva Backend - Multi-Agent Civic Issue Management Platform

A comprehensive FastAPI backend for intelligent, civic issue management using multi-agent orchestration with 5 specialized agents.

## Architecture Overview

### 5 Core Multi-Agent Systems

1. **Agent 1: Multimodal Issue Intelligence**
   - Extracts text from voice/audio using NVIDIA speech-to-text
   - Analyzes images using NVIDIA vision LLM
   - Fuses multimodal context (vision + voice + location)
   - Classifies issue type and severity
   - Stores classification results

2. **Agent 2: Authority Router**
   - Extracts routing parameters from complaint
   - Determines routing rules by issue type & severity
   - Finds responsible official in department/ward
   - Assigns complaint with SLA timeframe
   - Notifies official via email/SMS

3. **Agent 3: Safety Heatmap & Analytics**
   - Fetches complaints for geospatial clustering
   - Clusters complaints using DBSCAN (500m default radius)
   - Calculates cluster risk scores
   - Extracts time-aware risk patterns
   - Generates heatmap visualizations

4. **Agent 4: Safer Route Advisor**
   - Generates base routes with waypoints
   - Queries safety incidents along route
   - Calculates per-segment risk scores
   - Applies user preferences (avoid dark areas, etc)
   - Generates and ranks alternative routes

5. **Agent 5: Autonomous Escalation**
   - Fetches overdue complaints (SLA exceeded)
   - Checks resolution progress
   - Generates escalation summaries using NVIDIA LLM
   - Escalates to higher authority
   - Sends escalation notifications
   - Runs hourly via Celery Beat

## Technology Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: MongoDB (with Motor async driver)
- **Task Queue**: Celery + Redis
- **ML/Clustering**: scikit-learn (DBSCAN)
- **Geospatial**: GeoPy
- **AI Integration**: NVIDIA NIM (mocked for demo)
- **Async**: asyncio, aiofiles
- **API Docs**: Swagger/OpenAPI (auto-generated)

## Project Structure

```
backend/
├── app/
│   ├── agents/              # 5 multi-agent orchestrators
│   │   ├── classification_agent.py
│   │   ├── routing_agent.py
│   │   ├── heatmap_agent.py
│   │   ├── route_advisor_agent.py
│   │   └── escalation_agent.py
│   ├── models/              # Pydantic models for MongoDB
│   │   ├── complaint.py
│   │   ├── ward.py
│   │   ├── safety.py
│   │   ├── route.py
│   │   ├── citizen.py
│   │   ├── official.py
│   │   └── escalation.py
│   ├── routers/             # FastAPI endpoints
│   │   ├── complaints.py    # POST /report (Agent 1 & 2)
│   │   ├── heatmap.py       # GET /heatmap/data (Agent 3)
│   │   ├── routes.py        # POST /safer-path (Agent 4)
│   │   └── escalation.py    # GET /queue (Agent 5)
│   ├── utils/               # Helper utilities
│   │   ├── geospatial.py    # Distance, clustering
│   │   ├── storage.py       # File uploads
│   │   ├── notifications.py # Email/SMS (mocked)
│   │   └── nvidia_nim.py    # NVIDIA API mocks
│   ├── tasks/
│   │   └── celery_tasks.py  # Async escalation task
│   ├── config.py            # Settings from .env
│   └── main.py              # FastAPI app setup
├── pyproject.toml           # Dependencies
├── .env.example             # Configuration template
└── README.md                # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- MongoDB (local or Atlas)
- Redis (for Celery)
- Git

### 2. Clone Repository

```bash
cd backend
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -e ".[dev]"
```

Or from pyproject.toml:
```bash
pip install fastapi uvicorn motor pymongo celery redis numpy scikit-learn httpx pydantic python-multipart python-dotenv langchain
```

### 5. Configure Environment

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env`:
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=nagarseva_db
REDIS_URL=redis://localhost:6379/0
DEBUG=True
ENVIRONMENT=development
```

### 6. Start MongoDB (if local)

```bash
mongod
```

### 7. Start Redis (if local)

```bash
redis-server
```

### 8. Run FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 9. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 10. Optional: Run Celery Worker (for escalation tasks)

In a separate terminal:

```bash
celery -A app.tasks.celery_tasks worker --loglevel=info
```

### 11. Optional: Run Celery Beat (scheduler)

In another terminal:

```bash
celery -A app.tasks.celery_tasks beat --loglevel=info
```

## API Endpoints

### Complaints (Agent 1 & 2)

**Submit Complaint** (triggers classification + routing)
```bash
curl -X POST "http://localhost:8000/api/complaints/report" \
  -F "citizen_id=cit_001" \
  -F "issue_title=Pothole on Main Street" \
  -F "issue_description=Large pothole causing accidents" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060" \
  -F "address=Main Street, Downtown" \
  -F "ward_id=ward_001" \
  -F "image_file=@photo.jpg" \
  -F "audio_file=@description.wav"
```

**Response:**
```json
{
  "complaint_id": "uuid",
  "status": "assigned",
  "issue_type": "pothole",
  "severity": "high",
  "assigned_to_official_id": "off_pw_001",
  "sla_days": 5,
  "message": "Complaint successfully submitted and assigned"
}
```

### Heatmap & Analytics (Agent 3)

**Get Safety Heatmap**
```bash
curl "http://localhost:8000/api/heatmap/data?days_lookback=30&ward_id=ward_001&eps_meters=500"
```

**Response:**
```json
{
  "status": "success",
  "total_clusters": 2,
  "clusters": [
    {
      "cluster_id": "cluster_0",
      "center_latitude": 40.7140,
      "center_longitude": -74.0065,
      "radius_meters": 450,
      "risk_score": 0.85,
      "incident_count": 5,
      "time_analysis": [...]
    }
  ]
}
```

### Safer Routes (Agent 4)

**Get Safer Route**
```bash
curl -X POST "http://localhost:8000/api/routes/safer-path" \
  -H "Content-Type: application/json" \
  -d '{
    "start_latitude": 40.7128,
    "start_longitude": -74.0060,
    "start_address": "Downtown",
    "end_latitude": 40.7580,
    "end_longitude": -73.9855,
    "end_address": "Midtown",
    "mode": "walking",
    "avoid_dark_areas": true,
    "prefer_main_roads": true
  }'
```

**Response:**
```json
{
  "status": "success",
  "total_routes": 3,
  "routes": [
    {
      "route_index": 1,
      "overall_safety_score": 0.92,
      "risk_level": "low",
      "estimated_duration_minutes": 25,
      "waypoints": [...],
      "segments": [...]
    }
  ]
}
```

### Escalation (Agent 5)

**Get Escalation Queue** (automatically checks for overdue complaints)
```bash
curl "http://localhost:8000/api/escalation/queue"
```

**Response:**
```json
{
  "status": "success",
  "total_overdue": 2,
  "total_escalated": 2,
  "escalations": [
    {
      "complaint_id": "comp_001",
      "escalation_level": 1,
      "target_official_id": "off_sup_001",
      "escalated_at": "2024-01-15T10:30:00"
    }
  ]
}
```

## Database Models

### Collections

- **complaints** - Issue reports with classification & assignment
- **safety_clusters** - Geospatial incident clusters
- **safer_routes** - Pre-computed or cached safer routes
- **escalation_records** - Escalation history and status
- **citizens** - Citizen profiles
- **officials** - Official/government staff profiles
- **wards** - Administrative ward data

### Example Complaint Document

```json
{
  "_id": "uuid",
  "citizen_id": "cit_001",
  "issue_title": "Pothole on Main Street",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "address": "Main Street, Downtown",
    "ward_id": "ward_001"
  },
  "classification": {
    "issue_type": "pothole",
    "severity": "high",
    "confidence": 0.89,
    "description": "Large pothole detected via vision analysis"
  },
  "status": "assigned",
  "assignment": {
    "official_id": "off_pw_001",
    "department": "Public_Works",
    "sla_days": 5,
    "expected_resolution": "2024-01-20"
  },
  "created_at": "2024-01-15T10:00:00Z"
}
```

## Configuration

### Environment Variables

See `.env.example` for all available options:

| Variable | Description | Default |
|----------|-------------|---------|
| MONGODB_URL | MongoDB connection string | mongodb://localhost:27017 |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| ENVIRONMENT | dev/production | development |
| DEBUG | Enable debug mode | True |
| ESCALATION_CHECK_INTERVAL_HOURS | How often to check for overdue | 1 |
| OVERDUE_COMPLAINT_DAYS | Days before escalation | 7 |
| DEFAULT_CLUSTERING_RADIUS_METERS | DBSCAN eps | 500 |

## Testing

### Run Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

## Deployment

### Docker

```bash
docker build -t nagarseva-backend .
docker run -p 8000:8000 --env-file .env nagarseva-backend
```

### Cloud Platforms

- **AWS**: Use API Gateway + Lambda, or ECS with RDS
- **GCP**: Cloud Run + Cloud Firestore
- **Azure**: App Service + Cosmos DB

## Performance Optimization

### Caching

- Cache heatmap data (generated once per day)
- Cache safer routes (computed once per origin-destination)
- Use Redis for session/token storage

### Database Indexing

```javascript
// Create in MongoDB:
db.complaints.createIndex({ "location": "2dsphere" })
db.complaints.createIndex({ "status": 1, "assigned_at": -1 })
db.safety_clusters.createIndex({ "center": "2dsphere" })
```

### Rate Limiting

Add rate limiting middleware for production:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

## Troubleshooting

### MongoDB Connection Error

```bash
# Check if MongoDB is running
mongosh
```

### Celery Not Running Tasks

```bash
# Ensure Redis is running
redis-cli ping

# Check Celery worker logs
celery -A app.tasks.celery_tasks worker --loglevel=debug
```

### Port 8000 Already in Use

```bash
# Use different port
uvicorn app.main:app --port 8001
```

## Contributing

1. Create feature branch: `git checkout -b feature/agent-improvement`
2. Make changes and test: `pytest`
3. Commit: `git commit -am 'Add new feature'`
4. Push: `git push origin feature/agent-improvement`
5. Submit PR

## License

MIT License - See LICENSE file

## Contact

For issues, questions, or feedback:
- Email: team@nagarseva.com
- GitHub Issues: [NagarSeva/backend](https://github.com/nagarseva/backend/issues)

## Roadmap

- [ ] MongoDB integration (currently mocked)
- [ ] Real NVIDIA NIM API integration
- [ ] GraphQL API layer
- [ ] WebSocket support for real-time updates
- [ ] Mobile push notifications
- [ ] Advanced machine learning for risk prediction
- [ ] Multi-language support
