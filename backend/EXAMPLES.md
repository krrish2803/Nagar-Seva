# NagarSeva Backend - API Examples

This document provides detailed examples of how to interact with each agent and API endpoint.

## Quick Start Examples

### 1. Report a Complaint (Agent 1 + 2)

Submit a civic issue with image and voice:

```bash
# Create test image
echo "fake image data" > test_image.jpg

# Create test audio
echo "fake audio data" > test_audio.wav

# Submit complaint with multimodal input
curl -X POST "http://localhost:8000/api/complaints/report" \
  -F "citizen_id=cit_001" \
  -F "issue_title=Large Pothole on Main Street" \
  -F "issue_description=A dangerous pothole causing vehicle damage" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060" \
  -F "address=42 Main Street, Downtown, New York, NY 10001" \
  -F "ward_id=ward_001" \
  -F "pin_code=10001" \
  -F "image_file=@test_image.jpg" \
  -F "audio_file=@test_audio.wav"
```

**Expected Response:**
```json
{
  "complaint_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "assigned",
  "issue_type": "pothole",
  "severity": "high",
  "assigned_to_official_id": "off_pw_001",
  "sla_days": 5,
  "message": "Complaint 550e8400-e29b-41d4-a716-446655440000 successfully submitted and assigned"
}
```

**What happens internally:**
1. **Agent 1** processes the image and voice:
   - Extracts voice text: "A dangerous pothole causing vehicle damage"
   - Analyzes image using vision LLM
   - Fuses context: location + vision + voice
   - Classifies: issue_type=pothole, severity=high

2. **Agent 2** handles assignment:
   - Routes to: Public Works department
   - Finds supervisor: Ramesh Kumar (off_pw_001)
   - Creates assignment with SLA: 5 days
   - Sends notification email to supervisor

---

### 2. Get Safety Heatmap (Agent 3)

Retrieve clustered incidents with risk analysis:

```bash
# Get heatmap for last 30 days
curl "http://localhost:8000/api/heatmap/data?days_lookback=30&ward_id=ward_001&eps_meters=500"

# With specific parameters
curl "http://localhost:8000/api/heatmap/data" \
  -G \
  -d "days_lookback=7" \
  -d "ward_id=ward_001" \
  -d "eps_meters=300"
```

**Expected Response:**
```json
{
  "status": "success",
  "generated_at": "2024-01-15T10:30:00.000000",
  "parameters": {
    "days_lookback": 30,
    "ward_id": "ward_001",
    "eps_meters": 500
  },
  "total_clusters": 2,
  "clusters": [
    {
      "cluster_id": "cluster_0",
      "center_latitude": 40.7140,
      "center_longitude": -74.0065,
      "radius_meters": 450,
      "point_count": 5,
      "risk_score": 0.85,
      "risk_level": "high",
      "incident_types": {
        "pothole": 3,
        "garbage": 2
      },
      "severity_distribution": {
        "critical": 0,
        "high": 3,
        "medium": 2,
        "low": 0
      },
      "time_analysis": [
        {
          "period": "morning",
          "incident_count": 2,
          "average_severity": 0.7,
          "peak_hours": [7, 8, 9]
        },
        {
          "period": "evening",
          "incident_count": 3,
          "average_severity": 0.85,
          "peak_hours": [17, 18, 19]
        }
      ],
      "first_incident_at": "2024-01-10T09:15:00",
      "last_incident_at": "2024-01-15T18:30:00"
    }
  ]
}
```

**What happens internally:**
1. **Agent 3** analyzes complaints:
   - Fetches last 30 days of complaints in ward_001
   - Clusters using DBSCAN (500m radius)
   - Calculates risk: severity × density
   - Analyzes time patterns: morning/afternoon/evening/night

---

### 3. Get Safer Route (Agent 4)

Get safety-optimized routes:

```bash
# Get safer route with preferences
curl -X POST "http://localhost:8000/api/routes/safer-path" \
  -H "Content-Type: application/json" \
  -d '{
    "start_latitude": 40.7128,
    "start_longitude": -74.0060,
    "start_address": "42 Main Street, Downtown",
    "end_latitude": 40.7580,
    "end_longitude": -73.9855,
    "end_address": "Central Park, Midtown",
    "mode": "walking",
    "avoid_dark_areas": true,
    "prefer_main_roads": true,
    "avoid_busy_areas": false
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "total_routes": 3,
  "routes": [
    {
      "route_index": 1,
      "start_latitude": 40.7128,
      "start_longitude": -74.0060,
      "start_address": "42 Main Street, Downtown",
      "end_latitude": 40.7580,
      "end_longitude": -73.9855,
      "end_address": "Central Park, Midtown",
      "mode": "walking",
      "waypoints": [
        {
          "latitude": 40.7128,
          "longitude": -74.0060,
          "order": 0,
          "distance_from_start_meters": 0
        },
        {
          "latitude": 40.7246,
          "longitude": -73.9949,
          "order": 1,
          "distance_from_start_meters": 1238
        }
      ],
      "total_distance_meters": 6500,
      "estimated_duration_minutes": 85,
      "overall_safety_score": 0.92,
      "risk_level": "low",
      "high_risk_zones": 0,
      "recommended_times": ["morning", "afternoon"]
    },
    {
      "route_index": 2,
      "overall_safety_score": 0.75,
      "risk_level": "medium"
    },
    {
      "route_index": 3,
      "overall_safety_score": 0.65,
      "risk_level": "medium"
    }
  ]
}
```

**What happens internally:**
1. **Agent 4** creates routes:
   - Generates base route with 5-10 waypoints
   - Queries safety clusters within 300m of route
   - Calculates risk for each segment
   - Applies preferences: avoid night travel, prefer main roads
   - Generates 2 alternative routes
   - Ranks all 3 routes by safety score

---

### 4. Check Escalation Queue (Agent 5)

Monitor and escalate overdue complaints:

```bash
# Get pending escalations
curl "http://localhost:8000/api/escalation/queue"

# Get count only
curl "http://localhost:8000/api/escalation/pending-count"

# Get escalation status for specific complaint
curl "http://localhost:8000/api/escalation/comp_001/status"
```

**Expected Response:**
```json
{
  "status": "success",
  "checked_at": "2024-01-15T10:30:00.000000",
  "total_overdue": 2,
  "total_escalated": 2,
  "escalations": [
    {
      "complaint_id": "comp_001",
      "escalation_level": 1,
      "target_official_id": "off_sup_001",
      "summary": "ESCALATION SUMMARY\n==================\nComplaint ID: comp_001\nIssue: Pothole on Main Street\nOriginal Severity: high\n\nProgress Status: No progress\nDays Overdue: 3\n\nReason for Escalation:\nThe complaint has exceeded the SLA timeframe without adequate progress.\nThe assigned official has not provided satisfactory updates.\n\nRecommended Action:\nEscalate to department head for immediate intervention.",
      "escalated_at": "2024-01-15T10:30:00"
    },
    {
      "complaint_id": "comp_002",
      "escalation_level": 1,
      "target_official_id": "off_sup_001",
      "escalated_at": "2024-01-15T10:30:00"
    }
  ],
  "errors": []
}
```

**What happens internally (runs hourly via Celery):**
1. **Agent 5** escalates:
   - Fetches complaints overdue by 7+ days
   - Checks progress: no updates? → escalate
   - Generates summary using NVIDIA LLM
   - Escalates to ward supervisor (level 1)
   - Sends email to supervisor
   - Records escalation in DB

---

## Advanced Examples

### Filter Complaints by Status

```bash
curl "http://localhost:8000/api/complaints/?status=assigned&ward_id=ward_001&skip=0&limit=10"
```

### Get Heatmap Analytics

```bash
# Risk distribution
curl "http://localhost:8000/api/heatmap/analytics/risk-distribution?days_lookback=30&ward_id=ward_001"

# Incident types
curl "http://localhost:8000/api/heatmap/analytics/incident-types?days_lookback=30"

# Time patterns
curl "http://localhost:8000/api/heatmap/analytics/time-patterns?days_lookback=30"
```

### Analyze Route by Time of Day

```bash
curl "http://localhost:8000/api/routes/time-analysis" \
  -G \
  -d "start_latitude=40.7128" \
  -d "start_longitude=-74.0060" \
  -d "end_latitude=40.7580" \
  -d "end_longitude=-73.9855"
```

### Manually Escalate a Complaint

```bash
curl -X POST "http://localhost:8000/api/escalation/manual/comp_001" \
  -G \
  -d "escalation_level=2" \
  -d "reason=Inadequate progress by field supervisor"
```

---

## Python Client Examples

### Using requests library

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Submit complaint
files = {
    'image_file': open('photo.jpg', 'rb'),
    'audio_file': open('description.wav', 'rb')
}
data = {
    'citizen_id': 'cit_001',
    'issue_title': 'Pothole on Main Street',
    'issue_description': 'Large hole in road',
    'latitude': 40.7128,
    'longitude': -74.0060,
    'address': '42 Main Street, Downtown',
    'ward_id': 'ward_001'
}

response = requests.post(
    f"{BASE_URL}/api/complaints/report",
    data=data,
    files=files
)
complaint = response.json()
print(f"Complaint ID: {complaint['complaint_id']}")

# 2. Get heatmap
response = requests.get(
    f"{BASE_URL}/api/heatmap/data",
    params={'days_lookback': 30, 'ward_id': 'ward_001'}
)
heatmap = response.json()
print(f"Clusters found: {heatmap['total_clusters']}")

# 3. Get safer route
route_request = {
    'start_latitude': 40.7128,
    'start_longitude': -74.0060,
    'start_address': 'Downtown',
    'end_latitude': 40.7580,
    'end_longitude': -73.9855,
    'end_address': 'Midtown',
    'mode': 'walking',
    'avoid_dark_areas': True
}
response = requests.post(
    f"{BASE_URL}/api/routes/safer-path",
    json=route_request
)
routes = response.json()
print(f"Routes available: {routes['total_routes']}")
print(f"Safest route score: {routes['routes'][0]['overall_safety_score']}")

# 4. Check escalations
response = requests.get(f"{BASE_URL}/api/escalation/queue")
escalations = response.json()
print(f"Overdue complaints: {escalations['total_overdue']}")
```

### Using httpx (async)

```python
import httpx
import asyncio

async def get_heatmap():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/heatmap/data",
            params={'days_lookback': 30}
        )
        return response.json()

result = asyncio.run(get_heatmap())
print(result)
```

---

## Testing Workflow

### Complete End-to-End Flow

```bash
# 1. Start backend
uvicorn app.main:app --reload

# 2. Submit complaint (triggers Agent 1 & 2)
COMPLAINT=$(curl -s -X POST "http://localhost:8000/api/complaints/report" \
  -F "citizen_id=cit_test" \
  -F "issue_title=Test Pothole" \
  -F "issue_description=Test Description" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060" \
  -F "address=Test Street" \
  -F "ward_id=ward_001")

echo "Complaint: $COMPLAINT"

# 3. Check heatmap immediately (Agent 3)
curl -s "http://localhost:8000/api/heatmap/data?days_lookback=1" | jq .

# 4. Request safer route (Agent 4)
curl -s -X POST "http://localhost:8000/api/routes/safer-path" \
  -H "Content-Type: application/json" \
  -d '{
    "start_latitude": 40.7128,
    "start_longitude": -74.0060,
    "start_address": "Test Start",
    "end_latitude": 40.7580,
    "end_longitude": -73.9855,
    "end_address": "Test End",
    "mode": "walking"
  }' | jq .

# 5. Check escalations (Agent 5 - runs hourly)
curl -s "http://localhost:8000/api/escalation/queue" | jq .

# 6. Check API docs
# Open http://localhost:8000/docs in browser
```

---

## Troubleshooting

### "Connection refused" error

```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it:
uvicorn app.main:app --reload --port 8000
```

### Missing MongoDB/Redis

```bash
# Start Docker containers
docker-compose up -d

# Verify services are running
docker ps
```

### File upload fails

```bash
# Ensure uploads directory exists
mkdir -p uploads

# Check permissions
ls -la uploads/
```

### Celery tasks not running

```bash
# Start Celery worker
celery -A app.tasks.celery_tasks worker --loglevel=info

# Start Celery beat
celery -A app.tasks.celery_tasks beat --loglevel=info

# Check Redis
redis-cli ping  # Should return PONG
```

---

## Performance Testing

### Load testing with Apache Bench

```bash
# Test health endpoint
ab -n 100 -c 10 http://localhost:8000/health

# Test heatmap endpoint
ab -n 50 -c 5 http://localhost:8000/api/heatmap/data
```

### Using wrk

```bash
wrk -t4 -c100 -d30s http://localhost:8000/api/heatmap/data
```

---

## Security Notes

- Always use HTTPS in production
- Validate file uploads (size, type)
- Implement rate limiting
- Use API keys for official/admin endpoints
- Store sensitive data (NVIDIA keys) in secure vaults
- Enable CORS only for trusted domains
