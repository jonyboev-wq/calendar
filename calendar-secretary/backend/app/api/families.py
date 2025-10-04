from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.event import TaskFamily

router = APIRouter()


@router.get("", response_model=list[dict])
async def list_families(db: Session = Depends(get_db)) -> list[dict]:
    families = db.query(TaskFamily).all()
    return [
        {
            "key": family.key,
            "name": family.name,
            "weight": family.weight,
            "min_daily_minutes": family.min_daily_minutes,
            "weekly_target_minutes": family.weekly_target_minutes,
            "max_daily_minutes": family.max_daily_minutes,
        }
        for family in families
    ]


@router.post("", response_model=dict)
async def upsert_family(payload: dict, db: Session = Depends(get_db)) -> dict:
    key = payload.get("key")
    if not key:
        raise HTTPException(status_code=400, detail="key is required")
    family = db.query(TaskFamily).filter(TaskFamily.key == key).one_or_none()
    if family is None:
        family = TaskFamily(key=key)
    for field in ("name", "weight", "min_daily_minutes", "weekly_target_minutes", "max_daily_minutes"):
        if field in payload:
            setattr(family, field, payload[field])
    db.add(family)
    db.commit()
    db.refresh(family)
    return {
        "key": family.key,
        "name": family.name,
        "weight": family.weight,
        "min_daily_minutes": family.min_daily_minutes,
        "weekly_target_minutes": family.weekly_target_minutes,
        "max_daily_minutes": family.max_daily_minutes,
    }
