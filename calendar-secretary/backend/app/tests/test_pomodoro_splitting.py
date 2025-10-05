from datetime import datetime, timedelta
from uuid import uuid4

from types import SimpleNamespace

from app.services.planner.heuristic_solver import HeuristicPlanner


class DummyEvent:
    def __init__(self, duration_min: int, pomodoro_opt_in: bool = False):
        self.id = uuid4()
        self.duration_min = duration_min
        self.priority = 5
        self.family_key = None
        self.pomodoro_opt_in = pomodoro_opt_in


def test_pomodoro_flag_is_acknowledged():
    settings = SimpleNamespace(enabled=True, pomodoro_len_min=25, short_break_min=5, long_break_min=15, long_break_every=4)
    event = DummyEvent(180, pomodoro_opt_in=True)
    solver = HeuristicPlanner()
    plan = solver.solve([event], {}, settings, datetime.utcnow(), datetime.utcnow() + timedelta(hours=6))
    assert str(plan.scheduled[0].event_id) == str(event.id)
