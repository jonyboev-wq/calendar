from datetime import datetime, timedelta
from uuid import uuid4

from app.services.planner.heuristic_solver import HeuristicPlanner


class DummyEvent:
    def __init__(self, duration_min: int, depends_on: list | None = None):
        self.id = uuid4()
        self.duration_min = duration_min
        self.priority = 5
        self.family_key = None
        self.depends_on = depends_on or []


def test_fs_dependency_greedy_order():
    a = DummyEvent(60)
    b = DummyEvent(120, depends_on=[{"task_id": str(a.id), "type": "FS", "lag_min": 30}])
    solver = HeuristicPlanner()
    plan = solver.solve([a, b], {}, None, datetime.utcnow(), datetime.utcnow() + timedelta(hours=6))
    assert plan.scheduled[0].event_id == str(a.id)
    assert plan.scheduled[1].event_id == str(b.id)
