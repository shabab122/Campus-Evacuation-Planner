from __future__ import annotations

from .grid import Grid


def calculate_path_cost(grid: Grid, path: list[tuple[int, int]] | None) -> int | None:
    if not path:
        return None
    return sum(grid.get_cost(position) for position in path[1:])
