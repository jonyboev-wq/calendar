from __future__ import annotations

from typing import Any

from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.event import Event


class CalDAVClient:
    """Simplified CalDAV client wrapper.

    The real implementation would use the `caldav` library to communicate with
    Apple's iCloud. We store encrypted credentials and provide placeholder pull/push
    behaviours so the surrounding system can be tested without external access.
    """

    def __init__(self, db: Session):
        self.db = db
        if not settings.encryption_key:
            raise RuntimeError("encryption_key must be configured for CalDAV")
        self.cipher = Fernet(settings.encryption_key.encode("utf-8"))
        self._encrypted_credentials: bytes | None = None

    def save_credentials(self, credentials: dict[str, str]) -> None:
        blob = str(credentials).encode("utf-8")
        self._encrypted_credentials = self.cipher.encrypt(blob)

    def verify_connection(self) -> None:  # pragma: no cover - placeholder network call
        if not self._encrypted_credentials:
            raise RuntimeError("Credentials not provided")

    def pull_events(self) -> int:
        return self.db.query(Event).count()

    def push_events(self) -> int:
        return self.db.query(Event).count()
