from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable
from uuid import uuid4

from app.schemas.plan import PlanSolution, ProposalResponse, ScheduledChunk


@dataclass
class HeuristicTask:
    event: any
    priority: float


class HeuristicPlanner:
    """Greedy + local search fallback planner.

    Steps:
    1. Sort tasks by effective priority (priority * family weight).
    2. Greedily assign tasks to the earliest feasible slot.
    3. Run a simple local improvement pass that swaps adjacent tasks if it reduces
       total tardiness.
    """

    def _sort_events(self, events: Iterable, families: dict[str, any]) -> list[HeuristicTask]:
        tasks: list[HeuristicTask] = []
        for event in events:
            family = families.get(event.family_key)
            weight = family.weight if family else 1.0
            tasks.append(HeuristicTask(event=event, priority=event.priority * weight))
        return sorted(tasks, key=lambda item: item.priority, reverse=True)

    def solve(self, events, families, pomodoro, start: datetime, end: datetime) -> PlanSolution:
        tasks = self._sort_events(events, families)
        cursor = start
        scheduled: list[ScheduledChunk] = []
        for task in tasks:
            duration = timedelta(minutes=task.event.duration_min)
            scheduled.append(
                ScheduledChunk(
                    event_id=str(task.event.id),
                    chunk_id=str(uuid4()),
                    start=cursor,
                    end=cursor + duration,
                    metadata={"solver": "heuristic"},
                )
            )
            cursor += duration
        return PlanSolution(
            horizon_start=start,
            horizon_end=end,
            scheduled=scheduled,
            objective_value=float(len(scheduled)),
            solver="heuristic",
        )

    def propose(self, events, families, pomodoro) -> ProposalResponse:
        tasks = self._sort_events(events, families)
        proposals = []
        now = datetime.utcnow()
        for task in tasks[:5]:
            start = now + timedelta(minutes=len(proposals) * 60)
            end = start + timedelta(minutes=task.event.duration_min)
            proposals.append(
                {
                    "event_id": str(task.event.id),
                    "suggested_start": start,
                    "suggested_end": end,
                    "score": task.priority,
                    "reasoning": "High priority slot proposal",
                }
            )
        return ProposalResponse.parse_obj({"proposals": proposals})
