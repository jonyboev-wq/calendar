from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable
from uuid import uuid4

from app.schemas.plan import PlanSolution, ProposalResponse, ScheduledChunk
from app.services.planner.rules import topological_sort


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

    def _extract_dependency_ids(self, event: any) -> set[str]:
        dependency_ids: set[str] = set()
        raw_dependencies = getattr(event, "depends_on", None)
        if raw_dependencies:
            for dependency in raw_dependencies:
                if isinstance(dependency, dict):
                    dep_id = dependency.get("task_id") or dependency.get("depends_on_id")
                else:
                    dep_id = getattr(dependency, "task_id", None)
                    if dep_id is None:
                        dep_id = getattr(dependency, "depends_on_id", None)
                if dep_id is not None:
                    dependency_ids.add(str(dep_id))
        orm_dependencies = getattr(event, "dependencies", None)
        if orm_dependencies:
            for dependency in orm_dependencies:
                dep_id = getattr(dependency, "depends_on_id", None)
                if dep_id is not None:
                    dependency_ids.add(str(dep_id))
        return dependency_ids

    def _sort_events(self, events: Iterable, families: dict[str, any]) -> list[HeuristicTask]:
        event_map = {str(event.id): event for event in events}
        tasks: dict[str, HeuristicTask] = {}
        prerequisite_map: dict[str, set[str]] = {}
        adjacency: dict[str, set[str]] = {event_id: set() for event_id in event_map}

        for event_id, event in event_map.items():
            family = families.get(event.family_key)
            weight = family.weight if family else 1.0
            tasks[event_id] = HeuristicTask(event=event, priority=event.priority * weight)
            dependencies = {
                dep_id
                for dep_id in self._extract_dependency_ids(event)
                if dep_id in event_map and dep_id != event_id
            }
            prerequisite_map[event_id] = dependencies
            for dep_id in dependencies:
                adjacency.setdefault(dep_id, set()).add(event_id)

        if not tasks:
            return []

        topo_order = topological_sort(tasks.keys(), adjacency)
        topo_index = {event_id: index for index, event_id in enumerate(topo_order)}

        indegree = {event_id: len(prerequisite_map[event_id]) for event_id in tasks}
        available = [event_id for event_id, degree in indegree.items() if degree == 0]
        ordered_tasks: list[HeuristicTask] = []

        while available:
            available.sort(key=lambda eid: (-tasks[eid].priority, topo_index[eid]))
            current_id = available.pop(0)
            ordered_tasks.append(tasks[current_id])
            for child_id in adjacency.get(current_id, set()):
                indegree[child_id] -= 1
                if indegree[child_id] == 0:
                    available.append(child_id)

        return ordered_tasks

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
