from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import db as db_module
from app.core.db import Base, get_db
from app.main import app
from app.models.event import Event
from app.models.user import User


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

    db_module.engine = engine
    db_module.SessionLocal = TestingSessionLocal

    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        session.add(
            User(
                id=uuid4(),
                email="user@example.com",
                hashed_password="secret",
            )
        )
        session.commit()

    def override_get_db():
        database = TestingSessionLocal()
        try:
            yield database
        finally:
            database.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_event_with_time_window_persists(client):
    start = datetime.utcnow()
    end = start + timedelta(hours=1)

    payload = {
        "title": "Interview",
        "type": "flexible",
        "duration_min": 60,
        "priority": 5,
        "deadline": None,
        "time_windows": [
            {
                "start": start.isoformat(),
                "end": end.isoformat(),
            }
        ],
        "flex": None,
        "location": None,
        "travel_time_min": 0,
        "calendar_id": None,
        "external_ids": None,
        "constraints": None,
        "metadata": None,
        "family_key": None,
        "pomodoro_opt_in": False,
        "depends_on": [],
    }

    response = client.post("/api/events", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["time_windows"][0]["start"].startswith(start.isoformat(timespec="seconds"))

    with db_module.SessionLocal() as session:
        event = session.query(Event).one()
        assert event.time_windows[0]["start"].startswith(start.isoformat())
