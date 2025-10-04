from datetime import datetime, timedelta
from uuid import uuid4

from app.services.planner.heuristic_solver import HeuristicPlanner


class DummyEvent:
    def __init__(self, duration_min: int):
        self.id = uuid4()
        self.duration_min = duration_min
        self.priority = 5
        self.family_key = None


def test_replan_moves_next_event():
    solver = HeuristicPlanner()
    events = [DummyEvent(30), DummyEvent(60)]
    now = datetime.utcnow()
    plan = solver.solve(events, {}, None, now, now + timedelta(hours=2))
    assert plan.scheduled[0].start == now
    assert plan.scheduled[1].start == now + timedelta(minutes=30)
