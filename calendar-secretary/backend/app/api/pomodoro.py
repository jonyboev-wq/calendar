from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.event import UserPomodoroSettings

router = APIRouter()


@router.get("/me", response_model=dict)
async def get_me_settings(db: Session = Depends(get_db)) -> dict:
    settings = db.query(UserPomodoroSettings).first()
    if settings is None:
        return {
            "enabled": False,
            "pomodoro_len_min": 25,
            "short_break_min": 5,
            "long_break_min": 15,
            "long_break_every": 4,
        }
    return {
        "enabled": settings.enabled,
        "pomodoro_len_min": settings.pomodoro_len_min,
        "short_break_min": settings.short_break_min,
        "long_break_min": settings.long_break_min,
        "long_break_every": settings.long_break_every,
    }


@router.put("/me", response_model=dict)
async def update_me_settings(payload: dict, db: Session = Depends(get_db)) -> dict:
    settings = db.query(UserPomodoroSettings).first()
    if settings is None:
        raise HTTPException(status_code=404, detail="User not configured for Pomodoro")
    for field in ("enabled", "pomodoro_len_min", "short_break_min", "long_break_min", "long_break_every"):
        if field in payload:
            setattr(settings, field, payload[field])
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return {
        "enabled": settings.enabled,
        "pomodoro_len_min": settings.pomodoro_len_min,
        "short_break_min": settings.short_break_min,
        "long_break_min": settings.long_break_min,
        "long_break_every": settings.long_break_every,
    }
