from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Iterable


Coord = tuple[int, int]

NORMAL_COST = 1
CROWD_COST = 3
SMOKE_COST = 8
WALL_VALUE = -1
FIRE_VALUE = -2


class Grid:
    """Weighted floor map with emergency exits and an optional fallback staircase."""

    def __init__(
        self,
        file_path: str | Path,
        *,
        start: Coord | None = None,
        scenario: dict | None = None,
    ) -> None:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.rows = int(data["rows"])
        self.cols = int(data["cols"])
        self.locations = {
            name: tuple(position) for name, position in data.get("locations", {}).items()
        }
        self.start: Coord = tuple(start or data["start"])

        exits = data.get("exits")
        if exits is None:
            exits = [data["exit"]]
        self.exits: list[Coord] = [tuple(position) for position in exits]
        if not self.exits:
            raise ValueError("At least one exit is required")
        self.exit: Coord = self.exits[0]  # Week-1 compatibility.
        stairs = data.get("central_stairs")
        self.central_stairs: Coord | None = tuple(stairs) if stairs is not None else None

        self.base_grid: list[list[int]] = copy.deepcopy(data["grid"])
        self.grid: list[list[int]] = copy.deepcopy(self.base_grid)
        self.hazards: dict[Coord, str] = {}

        self._validate_shape()
        self._validate_special_cells()
        if scenario:
            self.apply_scenario(scenario)

    def _validate_shape(self) -> None:
        if self.rows < 1 or self.cols < 1:
            raise ValueError("Map dimensions must be positive")
        if len(self.grid) != self.rows or any(len(row) != self.cols for row in self.grid):
            raise ValueError("Map dimensions do not match rows and cols")
        for row in self.grid:
            for value in row:
                if type(value) is not int or (value < 1 and value not in {WALL_VALUE, FIRE_VALUE}):
                    raise ValueError("Cell costs must be positive integers, or -1/-2 for blocked cells")

    def _validate_special_cells(self) -> None:
        if not self.is_valid_position(self.start) or self.is_blocked(self.start):
            raise ValueError("Start position must be a walkable map cell")
        if not self.exits:
            raise ValueError("At least one exit is required")
        for exit_position in self.exits:
            if not self.is_valid_position(exit_position) or self.is_blocked(exit_position):
                raise ValueError(f"Exit {exit_position} must be a walkable map cell")
        if self.central_stairs is not None:
            if not self.is_valid_position(self.central_stairs) or self.is_blocked(self.central_stairs):
                raise ValueError("Central stairs must be a walkable cell in the base map")
            if self.central_stairs in self.exits:
                raise ValueError("Central stairs must be separate from emergency exits")

    def is_valid_position(self, position: Coord) -> bool:
        if len(position) != 2 or any(type(value) is not int for value in position):
            return False
        row, col = position
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_blocked(self, position: Coord) -> bool:
        if not self.is_valid_position(position):
            raise ValueError(f"Cell {position} is outside the map or has invalid coordinates")
        row, col = position
        return self.grid[row][col] in {WALL_VALUE, FIRE_VALUE}

    def get_neighbors(self, position: Coord) -> list[Coord]:
        if self.is_blocked(position):
            return []
        row, col = position
        candidates = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]
        return [
            candidate
            for candidate in candidates
            if self.is_valid_position(candidate) and not self.is_blocked(candidate)
        ]

    def get_cost(self, position: Coord) -> int:
        if self.is_blocked(position):
            raise ValueError(f"Blocked cell {position} has no movement cost")
        row, col = position
        return int(self.grid[row][col])

    def apply_scenario(self, scenario: dict) -> None:
        self.grid = copy.deepcopy(self.base_grid)
        self.hazards = {}
        self._apply_cells(scenario.get("crowd", []), "crowd", CROWD_COST)
        self._apply_cells(scenario.get("smoke", []), "smoke", SMOKE_COST)
        self._apply_cells(scenario.get("blocked", []), "blocked", WALL_VALUE)
        self._apply_cells(scenario.get("fire", []), "fire", FIRE_VALUE)

    def add_custom_hazards(
        self,
        *,
        crowd: Iterable[Coord] = (),
        smoke: Iterable[Coord] = (),
        fire: Iterable[Coord] = (),
        blocked: Iterable[Coord] = (),
    ) -> None:
        additions = [
            (crowd, "crowd", CROWD_COST),
            (smoke, "smoke", SMOKE_COST),
            (blocked, "blocked", WALL_VALUE),
            (fire, "fire", FIRE_VALUE),
        ]
        for cells, label, value in additions:
            for raw_position in cells:
                position = tuple(raw_position)
                if position in self.hazards:
                    raise ValueError(
                        f"Cell {position} already contains {self.hazards[position]} in the selected scenario"
                    )
                self._apply_cells([position], label, value)

    def _apply_cells(self, cells: Iterable[Coord | list[int]], label: str, value: int) -> None:
        for raw_position in cells:
            position = tuple(raw_position)
            if len(position) != 2 or any(type(value) is not int for value in position):
                raise ValueError(f"Invalid {label} coordinate: {raw_position}")
            row, col = position
            if not self.is_valid_position(position):
                raise ValueError(f"{label.title()} cell {position} is outside the map")
            if self.base_grid[row][col] == WALL_VALUE:
                raise ValueError(f"{label.title()} cell {position} is a wall")
            if position == self.start:
                raise ValueError(f"Start {position} cannot be changed into a hazard")
            self.grid[row][col] = value
            self.hazards[position] = label

    def hazard_type(self, position: Coord) -> str | None:
        if position in self.hazards:
            return self.hazards[position]
        row, col = position
        return "fire" if self.grid[row][col] == FIRE_VALUE else None
