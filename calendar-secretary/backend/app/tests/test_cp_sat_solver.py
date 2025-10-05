from datetime import datetime, timedelta
from uuid import uuid4

from app.services.planner.cp_sat_solver import CPSATSolver


class DummyEvent:
    def __init__(self, duration_min: int, priority: int):
        self.id = uuid4()
        self.duration_min = duration_min
        self.priority = priority
        self.type = "flexible"
        self.time_windows = []


def test_solver_prioritises_high_weight_when_time_limited():
    solver = CPSATSolver()
    start = datetime.utcnow()
    end = start + timedelta(hours=1)
    low_priority = DummyEvent(60, priority=1)
    high_priority = DummyEvent(60, priority=10)

    solution = solver.solve(
        [low_priority, high_priority],
        families={},
        pomodoro=None,
        start=start,
        end=end,
    )

    assert solution is not None
    assert len(solution.scheduled) == 1
    assert str(solution.scheduled[0].event_id) == str(high_priority.id)
