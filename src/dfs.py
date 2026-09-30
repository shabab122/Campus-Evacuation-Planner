def dfs(grid, *, return_trace: bool = False):
    start = grid.start
    goals = set(grid.exits)
    stack = [start]
    visited = {start}
    came_from = {}
    exploration_order = []

    while stack:
        current = stack.pop()
        exploration_order.append(current)
        if current in goals:
            path = reconstruct_path(came_from, current)
            return _result(path, exploration_order, return_trace)

        for neighbor in reversed(grid.get_neighbors(current)):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)

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
