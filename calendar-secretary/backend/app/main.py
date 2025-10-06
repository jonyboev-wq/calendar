import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.api import events, plan, sync
from app.api import families, pomodoro
from app.core.config import settings
from app.core import db as db_module
from app.models.event import UserPomodoroSettings
from app.models.user import User

logger = logging.getLogger(__name__)

RETRY_ATTEMPTS = 10
RETRY_SLEEP_SECONDS = 1.0

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


def _ensure_default_user() -> None:
    with db_module.SessionLocal() as session:
        user = session.query(User).first()
        if user is None:
            user = User(
                email="demo@example.com",
                hashed_password="demo",  # Placeholder for demo environments
            )
            session.add(user)
            session.flush()
        if session.query(UserPomodoroSettings).filter(UserPomodoroSettings.user_id == user.id).first() is None:
            session.add(UserPomodoroSettings(user_id=user.id))
        session.commit()


def _initialise_database() -> None:
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            db_module.Base.metadata.create_all(bind=db_module.engine)
            _ensure_default_user()
            if attempt > 1:
                logger.info("Connected to database after %s attempts", attempt)
            return
        except OperationalError as exc:  # pragma: no cover - startup safety net
            if attempt == RETRY_ATTEMPTS:
                logger.error("Database initialisation failed: %s", exc)
                raise
            logger.warning("Database not ready (attempt %s/%s): %s", attempt, RETRY_ATTEMPTS, exc)
            time.sleep(RETRY_SLEEP_SECONDS)


@app.on_event("startup")
def on_startup() -> None:
    _initialise_database()


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    """Landing endpoint for quick manual checks."""
    return {"status": "ok", "docs": "/docs", "health": "/health"}


@app.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    """Simple health-check endpoint for readiness probes."""
    return {"status": "ok"}
