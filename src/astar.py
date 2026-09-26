from __future__ import annotations

import heapq
from itertools import count

from .grid import Grid
from .heuristic import nearest_exit_distance


def a_star(grid: Grid, *, return_trace: bool = False):
    """Find the lowest weighted-cost route from start to any available exit.

    The Week-2 UI can request ``return_trace=True`` to animate the exact order
    in which nodes are expanded. The default return shape is kept compatible
    with the Week-1/early Week-2 code.
    """
    start = grid.start
    goals = set(grid.exits)
    sequence = count()

    open_set: list[tuple[int, int, int, tuple[int, int]]] = []
    heapq.heappush(
        open_set,
        (nearest_exit_distance(start, grid.exits), 0, next(sequence), start),
    )

    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score = {start: 0}
    exploration_order: list[tuple[int, int]] = []

    while open_set:
        _, current_cost, _, current = heapq.heappop(open_set)
        if current_cost != g_score.get(current):
            continue

        exploration_order.append(current)
        if current in goals:
            path = reconstruct_path(came_from, current)
            return _result(path, current_cost, exploration_order, return_trace)

        for neighbor in grid.get_neighbors(current):
            new_cost = current_cost + grid.get_cost(neighbor)
            if new_cost < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = new_cost
                came_from[neighbor] = current
                priority = new_cost + nearest_exit_distance(neighbor, grid.exits)
                heapq.heappush(
                    open_set,
                    (priority, new_cost, next(sequence), neighbor),
                )

    return _result(None, None, exploration_order, return_trace)


def _result(path, cost, exploration_order, return_trace):
    explored_nodes = len(exploration_order)
    if return_trace:
        return path, cost, explored_nodes, exploration_order
    return path, cost, explored_nodes


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
