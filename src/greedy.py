from __future__ import annotations

import heapq
from itertools import count

from .cost import calculate_path_cost
from .heuristic import nearest_exit_distance


def greedy_best_first(grid, *, return_trace: bool = False):
    start = grid.start
    goals = set(grid.exits)
    sequence = count()
    frontier = [(nearest_exit_distance(start, grid.exits), next(sequence), start)]
    visited = {start}
    came_from = {}
    exploration_order = []

    while frontier:
        _, _, current = heapq.heappop(frontier)
        exploration_order.append(current)
        if current in goals:
            path = reconstruct_path(came_from, current)
            cost = calculate_path_cost(grid, path)
            return _result(path, cost, exploration_order, return_trace)

        for neighbor in grid.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                priority = nearest_exit_distance(neighbor, grid.exits)
                heapq.heappush(frontier, (priority, next(sequence), neighbor))

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
