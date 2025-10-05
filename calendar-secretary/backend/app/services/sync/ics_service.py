from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.user import User


class ICSService:
    """Handle import/export of ICS files.

    For brevity this version performs a naive parse that treats each line starting
    with `SUMMARY:` as a new event. A production-ready implementation would use the
    `ics` or `icalendar` libraries and handle two-way synchronisation.
    """

    def __init__(self, db: Session):
        self.db = db

    def import_ics(self, data: bytes) -> int:
        text = data.decode("utf-8", errors="ignore")
        created = 0
        for line in text.splitlines():
            if line.startswith("SUMMARY:"):
                title = line.split(":", 1)[1]
                user = self.db.query(User).first()
                if user is None:
                    raise RuntimeError("User context required for ICS import")
                event = Event(
                    title=title,
                    type="fixed",
                    duration_min=60,
                    priority=5,
                    user_id=user.id,
                )
                self.db.add(event)
                created += 1
        self.db.commit()
        return created
