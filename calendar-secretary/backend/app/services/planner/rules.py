from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional


class TimeUtils:
    @staticmethod
    def to_minutes(dt: datetime) -> int:
        return int(dt.timestamp() // 60)

    @staticmethod
    def from_minutes(value: int) -> datetime:
        return datetime.utcfromtimestamp(value * 60)


class DependencyGraphError(RuntimeError):
    pass


def topological_sort(nodes: Iterable[str], edges: dict[str, set[str]]) -> list[str]:
    indegree = {node: 0 for node in nodes}
    for targets in edges.values():
        for target in targets:
            indegree[target] = indegree.get(target, 0) + 1
    queue = [node for node, degree in indegree.items() if degree == 0]
    order: list[str] = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for target in edges.get(node, set()):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(order) != len(nodes):
        raise DependencyGraphError("Dependency graph contains cycles")
    return order
