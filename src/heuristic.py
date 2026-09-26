from __future__ import annotations

from .grid import Coord


def manhattan_distance(current: Coord, goal: Coord) -> int:
    current_row, current_col = current
    goal_row, goal_col = goal
    return abs(current_row - goal_row) + abs(current_col - goal_col)


def nearest_exit_distance(current: Coord, exits: list[Coord]) -> int:
    if not exits:
        raise ValueError("At least one exit is required")
    return min(manhattan_distance(current, goal) for goal in exits)
