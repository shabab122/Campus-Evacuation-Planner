from __future__ import annotations

import heapq
from itertools import count


def ucs(grid, *, return_trace: bool = False):
    """Find the lowest-cost route to any exit using Uniform Cost Search.

    UCS expands the frontier node with the smallest accumulated path cost.
    Movement costs are supplied by the grid, so crowd and smoke penalties are
    respected while fire and wall cells remain blocked by the grid model.
    """
    start = grid.start
    goals = set(grid.exits)
    sequence = count()
    frontier = [(0, next(sequence), start)]
    costs = {start: 0}
    came_from = {}
    exploration_order = []

    while frontier:
        current_cost, _, current = heapq.heappop(frontier)
        if current_cost != costs.get(current):
            continue

        exploration_order.append(current)
        if current in goals:
            path = reconstruct_path(came_from, current)
            return _result(path, current_cost, exploration_order, return_trace)

        for neighbor in grid.get_neighbors(current):
            new_cost = current_cost + grid.get_cost(neighbor)
            if new_cost < costs.get(neighbor, float("inf")):
                costs[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(
                    frontier,
                    (new_cost, next(sequence), neighbor),
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