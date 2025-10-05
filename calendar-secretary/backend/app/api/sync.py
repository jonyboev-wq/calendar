from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.services.sync.caldav_client import CalDAVClient
from app.services.sync.ics_service import ICSService

router = APIRouter()


@router.post("/import/ics")
async def import_ics(data: bytes, db: Session = Depends(get_db)) -> dict[str, int]:
    if not settings.feature_ics_enabled:
        raise HTTPException(status_code=503, detail="ICS import disabled")
    service = ICSService(db)
    created = service.import_ics(data)
    return {"created": created}


@router.post("/caldav/connect")
async def connect_caldav(credentials: dict[str, str], db: Session = Depends(get_db)) -> dict[str, str]:
    if not settings.feature_caldav_enabled:
        raise HTTPException(status_code=503, detail="CalDAV disabled")
    client = CalDAVClient(db)
    client.save_credentials(credentials)
    client.verify_connection()
    return {"status": "connected"}


@router.post("/caldav/pull")
async def pull_caldav(db: Session = Depends(get_db)) -> dict[str, int]:
    client = CalDAVClient(db)
    imported = client.pull_events()
    return {"imported": imported}


@router.post("/caldav/push")
async def push_caldav(db: Session = Depends(get_db)) -> dict[str, int]:
    client = CalDAVClient(db)
    exported = client.push_events()
    return {"exported": exported}
