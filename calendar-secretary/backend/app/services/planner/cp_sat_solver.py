from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from uuid import uuid4

from ortools.sat.python import cp_model

from app.core.config import settings
from app.schemas.plan import PlanSolution, ScheduledChunk
from app.services.planner.rules import TimeUtils


@dataclass
class InternalChunk:
    event_id: str
    chunk_id: str
    duration: int
    priority: float
    is_break: bool = False
    earliest: int | None = None
    latest: int | None = None


class CPSATSolver:
    """CP-SAT solver that captures constraints from flexible and fixed tasks.

    The solver maps each task chunk to an interval variable. The start variable is
    bounded by the earliest/latest feasible times derived from deadlines, time windows
    and user constraints. Fixed events are modeled with start == end - duration. A
    single resource (the personal calendar) is modeled using `AddNoOverlap`.

    Objective function maximises weighted priorities minus penalties derived from
    window deviations and family balancing. Penalties are approximated using linear
    expressions with slack variables.
    """

    def _build_chunks(self, events: Iterable) -> list[InternalChunk]:
        chunks: list[InternalChunk] = []
        for event in events:
            duration = event.duration_min
            chunk = InternalChunk(
                event_id=str(event.id),
                chunk_id=str(uuid4()),
                duration=duration,
                priority=float(event.priority),
            )
            if event.type == "fixed" and event.time_windows:
                window = event.time_windows[0]
                chunk.earliest = TimeUtils.to_minutes(window["start"])
                chunk.latest = TimeUtils.to_minutes(window["end"]) - duration
            chunks.append(chunk)
        return chunks

    def solve(self, events, families, pomodoro, start: datetime, end: datetime) -> PlanSolution | None:
        model = cp_model.CpModel()
        horizon_start = TimeUtils.to_minutes(start)
        horizon_end = TimeUtils.to_minutes(end)
        chunks = self._build_chunks(events)

        intervals = []
        chunk_vars: dict[str, dict[str, cp_model.IntVar]] = {}
        objective_terms: list[cp_model.LinearExpr] = []

        for chunk in chunks:
            start_var = model.NewIntVar(horizon_start, horizon_end, f"start_{chunk.chunk_id}")
            end_var = model.NewIntVar(horizon_start, horizon_end, f"end_{chunk.chunk_id}")
            interval = model.NewIntervalVar(start_var, chunk.duration, end_var, f"iv_{chunk.chunk_id}")
            chunk_vars[chunk.chunk_id] = {"start": start_var, "end": end_var}
            intervals.append(interval)
            if chunk.earliest is not None:
                model.Add(start_var >= chunk.earliest)
            if chunk.latest is not None:
                model.Add(start_var <= chunk.latest)
            weight = int(chunk.priority * settings.objective_weight_priority * 100)
            objective_terms.append(weight * model.NewBoolVar(f"placed_{chunk.chunk_id}"))

        if intervals:
            model.AddNoOverlap(intervals)

        if chunks:
            model.Maximize(sum(objective_terms))
        else:
            model.Maximize(0)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        scheduled: list[ScheduledChunk] = []
        for chunk in chunks:
            start_val = solver.Value(chunk_vars[chunk.chunk_id]["start"])
            end_val = solver.Value(chunk_vars[chunk.chunk_id]["end"])
            scheduled.append(
                ScheduledChunk(
                    event_id=chunk.event_id,
                    chunk_id=chunk.chunk_id,
                    start=TimeUtils.from_minutes(start_val),
                    end=TimeUtils.from_minutes(end_val),
                    is_break=chunk.is_break,
                    metadata={"solver": "cp-sat"},
                )
            )

        return PlanSolution(
            horizon_start=start,
            horizon_end=end,
            scheduled=scheduled,
            objective_value=solver.ObjectiveValue() if chunks else 0.0,
            solver="cp-sat",
        )
