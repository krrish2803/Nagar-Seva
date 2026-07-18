# NagarSeva

NagarSeva is an AI-powered civic issue reporting platform that helps citizens report local problems faster and helps authorities classify, verify, route, track, and escalate complaints with better context.

## Problem Statement

Cities receive thousands of civic complaints about broken streetlights, unsafe roads, garbage, potholes, water leakage, and other public issues. Most reporting systems are slow, text-heavy, and difficult for elderly citizens or less tech-savvy users. Authorities also struggle with duplicate/fake complaints, poor evidence, manual routing, and lack of visibility into hotspots or delayed resolutions.

## Proposed Solution

NagarSeva provides a voice-first and photo-based complaint reporting flow where citizens can speak, upload evidence, and submit location details. AI agents transcribe and understand the complaint, classify the issue, calculate a trust score, route it to the correct authority, and generate simple progress updates. The platform also includes dashboards, PDF issue reports, escalation tracking, heatmap analytics, and safer civic intelligence workflows.

## Impact

- Makes complaint reporting faster, more accessible, and language-friendly for Indian citizens.
- Reduces authority workload by automating classification, routing, trust scoring, and progress summaries.
- Improves reliability by flagging low-trust reports and highlighting evidence quality.
- Helps city teams identify high-risk areas, unresolved clusters, and SLA breaches through analytics.

## Key Features

- **Voice-First Reporting Agent:** Upload a voice note and photo, then AI drafts and classifies the complaint.
- **AI Trust Scoring:** Evaluates photo quality, voice clarity, location accuracy, and evidence completeness.
- **Citizen Dashboard:** Shows report history, AI progress updates, trust score, uploaded media, status, and escalation state.
- **Authority Routing:** Routes issues by category, ward, department, severity, and SLA.
- **PDF Report Generation:** Creates a premium issue report with complaint details, location, ward, PIN, and uploaded image name.
- **Heatmap Analytics:** Visualizes risk clusters, incident distribution, time patterns, and safety insights.
- **Escalation Engine:** Tracks overdue complaints and escalates unresolved reports to higher authority levels.

## Tech Stack

### Frontend

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Browser PDF generation

### Backend

- FastAPI
- MongoDB Atlas with Motor/PyMongo
- JWT authentication
- NVIDIA NIM integration layer
- Celery + Redis support for background jobs
- scikit-learn DBSCAN for clustering

## File Structure

```text
Nagar Seva/
├── app/                         # Next.js app router pages and API proxy routes
│   ├── api/                     # Frontend proxy routes to backend
│   ├── auth/                    # Login page
│   ├── dashboard/               # Citizen dashboard
│   ├── upload/                  # Report upload page
│   ├── classification/          # AI classification page
│   ├── routing/                 # Authority routing page
│   ├── escalation/              # Escalation dashboard
│   └── heatmap/                 # Heatmap analytics page
├── components/                  # Landing page and shared UI components
├── lib/                         # Frontend helpers such as PDF generation
├── backend/
│   ├── app/
│   │   ├── agents/              # AI classification, routing, trust, heatmap, escalation agents
│   │   ├── models/              # Complaint, citizen, official, route, ward models
│   │   ├── routers/             # FastAPI endpoints
│   │   ├── schemas/             # Request/response schemas
│   │   ├── tasks/               # Celery task definitions
│   │   └── utils/               # Auth, database, storage, notifications, NVIDIA utilities
│   ├── tests/                   # Backend tests
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Backend container image
│   └── RENDER_DEPLOYMENT.md     # Render backend deployment guide
├── ARCHITECTURE.md              # Mermaid architecture and flow diagrams
├── render.yaml                  # Render Blueprint for backend deployment
├── package.json                 # Frontend dependencies and scripts
└── LICENSE                      # Open source license
```

## Prerequisites

- Node.js 18+
- Python 3.10+ or 3.11+
- MongoDB Atlas database
- NVIDIA API key
- Optional: Redis for Celery background workers

## Environment Variables

Create `backend/.env` for local backend development:

```env
MONGODB_URI=your-mongodb-atlas-uri
MONGODB_DATABASE=nagarseva_db
SECRET_KEY=replace-with-a-long-random-secret
NVIDIA_API_KEY=your-nvidia-api-key
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL_VISION=meta/llama-3.2-11b-vision-instruct
NVIDIA_MODEL_TEXT=meta/llama-3.1-70b-instruct
UPLOAD_DIR=./uploads
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
DEBUG=True
ENVIRONMENT=development
```

Create `.env.local` for frontend if the backend is not running on the default URL:

```env
BACKEND_API_BASE_URL=http://localhost:8001
NEXT_PUBLIC_BACKEND_API_BASE_URL=http://localhost:8001
```

For Netlify, set `NEXT_PUBLIC_BACKEND_API_BASE_URL` to the deployed Render backend URL so long-running upload requests go directly to FastAPI instead of timing out inside a Netlify function.

> Never commit real `.env` files or API keys.

## Installation

### 1. Install frontend dependencies

```bash
npm install
```

### 2. Install backend dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run Locally

### Start backend

From the `backend` directory:

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Backend runs at:

```text
http://localhost:8001
```

API docs:

```text
http://localhost:8001/docs
```

### Start frontend

From the project root:

```bash
npm run dev -- -p 3001
```

Frontend runs at:

```text
http://localhost:3001
```

## Useful Commands

```bash
# Frontend development
npm run dev -- -p 3001

# Frontend production build
npm run build

# Frontend production server
npm run start

# Backend development server
cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Backend tests
cd backend && pytest

# Backend syntax validation
python3 -m compileall backend/app
```

## Backend Deployment on Render

This project includes a backend-only Render Blueprint at `render.yaml`.

Required Render settings:

- **Root Directory:** `backend`
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health`

If the frontend is deployed on Netlify, include the Netlify URL in Render `CORS_ORIGINS`, for example:

```text
https://your-site.netlify.app,https://your-deploy-preview.netlify.app,http://localhost:3000,http://localhost:3001
```

The backend also supports Netlify deploy previews through `CORS_ORIGIN_REGEX`:

```text
https://([a-z0-9]+--)?nagar-seva\.netlify\.app
```

Read the full deployment guide:

```text
backend/RENDER_DEPLOYMENT.md
```

## Frontend Routes

- `/` — landing page
- `/auth` — authentication page
- `/dashboard` — citizen report dashboard
- `/upload` — upload report page
- `/classification` — AI classification page
- `/routing` — authority routing page
- `/escalation` — escalation dashboard
- `/heatmap` — heatmap analytics page

## Backend API Areas

- `/api/auth` — authentication and JWT login
- `/api/complaints` — complaint reporting, list, detail, status, citizen dashboard
- `/api/heatmap` — heatmap data and analytics
- `/api/routes` — safer route advisor
- `/api/escalation` — overdue complaint and escalation analytics
- `/health` — Render health check

## Architecture

See the Mermaid architecture and project flow diagrams in:

```text
ARCHITECTURE.md
```

## License

This project is open source under the MIT License. See `LICENSE`.
