# Simple Market FastAPI App

## Run locally

```bash
cd /backend
uv init
uv add "fastapi[standard]"
cd /backend/app
uv run -m uvicorn main:app --reload

# Docker Build
docker compose up --build
And you're good to go 🚀
