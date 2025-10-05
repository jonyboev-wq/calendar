from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import events, plan, sync
from app.api import families, pomodoro
from app.core.config import settings

app = FastAPI(title="Calendar Secretary", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(families.router, prefix="/api/families", tags=["families"])
app.include_router(plan.router, prefix="/api/plan", tags=["plan"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])
app.include_router(pomodoro.router, prefix="/api/users", tags=["pomodoro"])


@app.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    """Simple health-check endpoint for readiness probes."""
    return {"status": "ok"}
