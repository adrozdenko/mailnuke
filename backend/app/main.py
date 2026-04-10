"""MailNuke API server."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import presets, cleanup

app = FastAPI(title="MailNuke API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(presets.router, prefix="/api")
app.include_router(cleanup.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
