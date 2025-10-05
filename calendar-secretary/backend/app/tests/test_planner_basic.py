from datetime import datetime, timedelta
from uuid import uuid4

from app.schemas.plan import PlanSolution
from app.services.planner.heuristic_solver import HeuristicPlanner


class DummyEvent:
    def __init__(self, duration_min: int, priority: int = 5, family_key: str | None = None):
        self.id = uuid4()
        self.duration_min = duration_min
        self.priority = priority
        self.family_key = family_key


def test_heuristic_orders_by_priority():
    solver = HeuristicPlanner()
    events = [DummyEvent(60, priority=p) for p in (1, 10, 5)]
    plan = solver.solve(events, {}, None, datetime.utcnow(), datetime.utcnow() + timedelta(hours=5))
    assert isinstance(plan, PlanSolution)
    assert plan.scheduled[0].event_id == events[1].id
