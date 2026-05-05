from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_current_user
from app.config import settings

app = FastAPI(title="Bakebook API", version="0.0.1")

# CORS for local dev
if settings.env == "dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "version": "0.0.1"}


@app.get("/api/v1/me")
async def me(request: Request):
    email = get_current_user(request)
    return {"email": email}
