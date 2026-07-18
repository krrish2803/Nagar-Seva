# Deploy NagarSeva Backend on Render

This backend is a standalone FastAPI service. Deploy it separately from the Next.js frontend and point the frontend API base URL to the deployed Render URL.

## Option 1: Blueprint deploy

1. Push the repository to GitHub.
2. Open Render and choose **New > Blueprint**.
3. Select this repository.
4. Render will detect the root `render.yaml`.
5. Fill the secret environment variables in Render before the first deploy.

## Option 2: Manual web service

Use these Render settings:

- **Service type:** Web Service
- **Runtime:** Python
- **Root Directory:** `backend`
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health`

## Required environment variables

Set these in **Render Dashboard > Service > Environment**:

| Key | Value |
| --- | --- |
| `PYTHON_VERSION` | `3.11.9` |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `LOG_LEVEL` | `INFO` |
| `MONGODB_URI` | Your MongoDB Atlas connection string |
| `MONGODB_DATABASE` | `nagarseva_db` |
| `SECRET_KEY` | A long random secret, or let Render generate it from `render.yaml` |
| `NVIDIA_API_KEY` | Your NVIDIA API key |
| `NVIDIA_NIM_BASE_URL` | `https://integrate.api.nvidia.com/v1` |
| `NVIDIA_MODEL_VISION` | `meta/llama-3.2-11b-vision-instruct` |
| `NVIDIA_MODEL_TEXT` | `meta/llama-3.1-70b-instruct` |
| `UPLOAD_DIR` | `/tmp/nagarseva-uploads` |
| `CORS_ORIGINS` | Your frontend URL, plus local dev URLs if needed |
| `CORS_ORIGIN_REGEX` | `https://([a-z0-9]+--)?nagar-seva\.netlify\.app` |

Example `CORS_ORIGINS`:

```text
http://localhost:3000,http://localhost:3001,https://your-frontend-domain.vercel.app
```

## Frontend connection

After Render deploys, copy your backend URL, for example:

```text
https://nagarseva-backend.onrender.com
```

Set this in the frontend environment:

```text
BACKEND_API_BASE_URL=https://nagarseva-backend.onrender.com
```

Then redeploy or restart the frontend.

## Notes

- Render free instances sleep when inactive, so the first request can be slow.
- `/tmp/nagarseva-uploads` is ephemeral. Uploaded images can disappear after redeploys/restarts. For production media, use S3, Cloudinary, or a Render persistent disk.
- Celery background workers need a separate Render worker service and a managed Redis instance. The API web service can run without the worker for normal request/response flows.
- Keep `.env` files local only. The repository already ignores root and backend `.env` files.
