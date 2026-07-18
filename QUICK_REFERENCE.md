# NagarSeva - Quick Reference Card

## 🎯 One-Minute Overview

**What is it?** AI-powered civic grievance platform with intelligent routing, safety heatmaps, and autonomous escalation.

**Frontend?** Landing page at http://localhost:3001 ✅ (already running)  
**Backend?** FastAPI at http://localhost:8000 (ready to start)  
**API Docs?** http://localhost:8000/docs (Swagger interactive)

---

## ⚡ Start Everything

```bash
# Start backend + MongoDB + Redis (one command)
cd backend && docker-compose -f docker-compose-dev.yml up

# Then open:
# Frontend: http://localhost:3001
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## 🧠 The 5 Agents

| Agent | Purpose | Endpoint | Input |
|-------|---------|----------|-------|
| **Classification** | Photo → Issue type | `POST /api/complaints/report` | Photo + audio + location |
| **Router** | Route to department | `POST /api/routing/assign` | Complaint ID |
| **Heatmap** | Safety clusters | `GET /api/heatmap/data` | Ward ID, time filter |
| **Route Advisor** | Safest path A→B | `POST /api/routes/safer-path` | Start/end location + prefs |
| **Escalation** | Auto-escalate overdue | Hourly Celery task | Runs automatically |

---

## 📞 Core API Calls

### 1. Report Issue
```bash
curl -X POST http://localhost:8000/api/complaints/report \
  -F "image=@pothole.jpg" \
  -F "audio=@description.wav" \
  -F "description=Large pothole" \
  -F "latitude=22.5726" \
  -F "longitude=88.3639" \
  -F "ward_id=kolkata_ward_1"
```

### 2. Get Safety Heatmap
```bash
curl http://localhost:8000/api/heatmap/data \
  "?ward_id=kolkata_ward_1&time_filter=night"
```

### 3. Get Safer Route
```bash
curl -X POST http://localhost:8000/api/routes/safer-path \
  -H "Content-Type: application/json" \
  -d '{
    "start_lat": 22.5726,
    "start_lng": 88.3639,
    "end_lat": 22.5800,
    "end_lng": 88.3700,
    "preferences": {
      "women_only_paths": true,
      "avoid_dark_areas": true
    }
  }'
```

### 4. Check Escalations
```bash
curl http://localhost:8000/api/escalation/queue
```

### 5. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "citizen_123", "role": "citizen"}'
```

---

## 📁 Where Everything Is

```
Frontend:        / (root directory)
Backend:         /backend
Docs:            /COMPLETE_SETUP_GUIDE.md (comprehensive)
                 /PROJECT_SUMMARY.md (architecture)
                 /DEPLOYMENT_CHECKLIST.md (production)
Tests:           /backend/tests/
Config:          /backend/.env.example
```

---

## 🧪 Run Tests

```bash
cd backend
pytest tests/ -v

# Individual test file:
pytest tests/test_classification_agent.py -v
```

---

## 🔧 Environment Setup

**Frontend:** No setup needed (uses defaults)

**Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env if using non-local MongoDB/Redis
```

**Key Variables:**
```
MONGODB_URL=mongodb://localhost:27017/nagarseva
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
```

---

## 🐳 Docker Commands

```bash
# Start everything
docker-compose -f backend/docker-compose-dev.yml up

# Stop everything
docker-compose -f backend/docker-compose-dev.yml down

# View logs
docker-compose -f backend/docker-compose-dev.yml logs -f

# Restart services
docker-compose -f backend/docker-compose-dev.yml restart
```

---

## 📊 Project Structure

```
NagarSeva/
├── components/           ← Frontend React components
├── app/                  ← Next.js app directory
├── backend/
│   ├── app/agents/       ← 5 AI agents
│   ├── app/routers/      ← API endpoints
│   ├── app/models/       ← MongoDB schemas
│   ├── app/schemas/      ← Request/response validation
│   ├── tests/            ← Unit tests
│   └── requirements.txt   ← Dependencies
└── COMPLETE_SETUP_GUIDE.md ← Full documentation
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Run: `docker-compose -f backend/docker-compose-dev.yml up` |
| "ModuleNotFoundError" | Run: `pip install -r backend/requirements.txt` |
| "Port 3000 in use" | Frontend automatically uses 3001 (no action needed) |
| "Celery tasks not running" | Start worker: `celery -A app.tasks.celery_tasks worker --loglevel=info` |
| "MongoDB error" | Run: `docker run -d -p 27017:27017 --name mongodb mongo:latest` |
| "Tests failing" | Run: `pip install -r backend/requirements.txt --force-reinstall` |

---

## ✅ Verification Checklist

After starting:

- [ ] Frontend loads at http://localhost:3001 ✅
- [ ] Backend API responds at http://localhost:8000 ✅
- [ ] Swagger docs at http://localhost:8000/docs ✅
- [ ] Can make request to `/api/heatmap/data` (GET) ✅
- [ ] Tests pass with `pytest tests/ -v` ✅
- [ ] MongoDB running: `docker ps | grep mongo` ✅
- [ ] Redis running: `docker ps | grep redis` ✅

---

## 📚 Documentation Map

| File | Contains |
|------|----------|
| **COMPLETE_SETUP_GUIDE.md** | Everything (start here) |
| **PROJECT_SUMMARY.md** | Architecture overview |
| **DEPLOYMENT_CHECKLIST.md** | Production readiness |
| **QUICK_REFERENCE.md** | This file (quick lookup) |
| **backend/README.md** | Backend deep-dive |
| **backend/QUICK_START.md** | Local dev setup |
| **backend/EXAMPLES.md** | API curl examples |
| **backend/PROJECT_SUMMARY.md** | 5-agent architecture |

---

## 🎯 Next Steps

1. **Now:** Run `docker-compose -f backend/docker-compose-dev.yml up`
2. **Next:** Visit `http://localhost:8000/docs` and test endpoints
3. **Then:** Read `COMPLETE_SETUP_GUIDE.md` for details
4. **Finally:** Deploy to cloud (AWS/GCP/Azure)

---

## 🚀 Tech Stack Summary

**Frontend:**
- Next.js 14 + React 18
- Tailwind CSS 3
- TypeScript

**Backend:**
- FastAPI + Uvicorn
- Python 3.10+
- MongoDB (Motor async driver)
- Celery + Redis
- NVIDIA NIM API (AI)

**DevOps:**
- Docker & Docker Compose
- Pytest for testing
- Git for version control

---

## 💡 Key Features

✅ AI-powered issue classification  
✅ Intelligent authority routing  
✅ Safety heatmaps with time-of-day awareness  
✅ Safer route recommendations  
✅ Autonomous escalation for overdue issues  
✅ Citizen complaint tracking  
✅ Ward responsiveness leaderboard  
✅ Real-time notifications  
✅ Full API documentation  
✅ Comprehensive tests  

---

## 🎓 Learning Path

1. **5 min:** Read this Quick Reference
2. **15 min:** Run `docker-compose up` and test via Swagger
3. **30 min:** Read `PROJECT_SUMMARY.md` for architecture
4. **1 hour:** Read `COMPLETE_SETUP_GUIDE.md` for full details
5. **2 hours:** Explore agent code in `backend/app/agents/`
6. **1 day:** Set up production deployment

---

## 📞 Support

- **Quick issues?** Check QUICK_REFERENCE.md (you're reading it!)
- **Setup help?** See COMPLETE_SETUP_GUIDE.md
- **API docs?** Visit http://localhost:8000/docs
- **Architecture?** Read PROJECT_SUMMARY.md
- **Deployment?** Check DEPLOYMENT_CHECKLIST.md

---

**Built with ❤️ for better civic governance**

*Last Updated: 2026-07-18*
