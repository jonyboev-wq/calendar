from datetime import datetime, timedelta
from uuid import uuid4

from types import SimpleNamespace

from app.services.planner.heuristic_solver import HeuristicPlanner


class DummyEvent:
    def __init__(self, duration_min: int, priority: int, family_key: str):
        self.id = uuid4()
        self.duration_min = duration_min
        self.priority = priority
        self.family_key = family_key


def test_family_weight_affects_order():
    health_family = SimpleNamespace(weight=1.4)
    study_family = SimpleNamespace(weight=1.0)
    families = {"health": health_family, "study": study_family}
    events = [
        DummyEvent(60, priority=6, family_key="health"),
        DummyEvent(60, priority=8, family_key="study"),
    ]
    solver = HeuristicPlanner()
    plan = solver.solve(events, families, None, datetime.utcnow(), datetime.utcnow() + timedelta(hours=4))
    assert str(plan.scheduled[0].event_id) == str(events[0].id)
