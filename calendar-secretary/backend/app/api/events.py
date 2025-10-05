from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.event import Event, TaskDependency
from app.models.user import User
from app.schemas.event import EventCreate, EventSchema, EventUpdate

router = APIRouter()


def _apply_dependencies(event: Event, depends_on: list[dict[str, Any]], db: Session) -> None:
    event.dependencies.clear()
    for dep in depends_on:
        dependency = TaskDependency(
            task_id=event.id,
            depends_on_id=dep["task_id"],
            type=dep.get("type", "FS"),
            lag_min=dep.get("lag_min", 0),
        )
        db.add(dependency)


@router.get("", response_model=list[EventSchema])
async def list_events(db: Session = Depends(get_db)) -> list[EventSchema]:
    events = db.query(Event).all()
    return [EventSchema.from_orm(event) for event in events]


@router.post("", response_model=EventSchema, status_code=201)
async def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> EventSchema:
    user = db.query(User).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User context missing")
    event = Event(user_id=user.id, **payload.dict(exclude={"depends_on"}))
    db.add(event)
    db.flush()
    _apply_dependencies(event, [dep.dict() for dep in payload.depends_on], db)
    db.commit()
    db.refresh(event)
    return EventSchema.from_orm(event)


@router.patch("/{event_id}", response_model=EventSchema)
async def update_event(
    event_id: UUID,
    payload: EventUpdate,
    db: Session = Depends(get_db),
) -> EventSchema:
    event = db.query(Event).filter(Event.id == event_id).one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    data = payload.dict(exclude_unset=True, exclude={"depends_on"})
    for key, value in data.items():
        setattr(event, key, value)
    if "depends_on" in payload.__fields_set__:
        _apply_dependencies(event, [dep.dict() for dep in payload.depends_on], db)
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventSchema.from_orm(event)
