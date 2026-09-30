from collections import deque


def bfs(grid, *, return_trace: bool = False):
    """Breadth-first search for the nearest exit by number of grid steps."""
    start = grid.start
    goals = set(grid.exits)
    queue = deque([start])
    visited = {start}
    came_from = {}
    exploration_order = []

    while queue:
        current = queue.popleft()
        exploration_order.append(current)
        if current in goals:
            path = reconstruct_path(came_from, current)
            return _result(path, exploration_order, return_trace)

        for neighbor in grid.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                came_from[neighbor] = current

    return _result(None, exploration_order, return_trace)


def _result(path, exploration_order, return_trace):
    explored_nodes = len(exploration_order)
    if return_trace:
        return path, explored_nodes, exploration_order
    return path, explored_nodes


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
