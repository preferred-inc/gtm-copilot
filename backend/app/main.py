from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import workspace, export, import_, auth, generate

app = FastAPI(title="GTM Copilot API", version="0.1.0")

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workspace.router)
app.include_router(export.router)
app.include_router(import_.router)
app.include_router(generate.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}
