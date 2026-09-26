from __future__ import annotations

import json
from pathlib import Path

from .grid import Coord, Grid


DEFAULT_MAP_PATH = Path("data/map.json")
DEFAULT_SCENARIOS_PATH = Path("data/scenarios.json")


def load_scenarios(file_path: str | Path = DEFAULT_SCENARIOS_PATH) -> dict[str, dict]:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_locations(file_path: str | Path = DEFAULT_MAP_PATH) -> dict[str, Coord]:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return {name: tuple(position) for name, position in data.get("locations", {}).items()}


def build_grid(
    scenario_name: str,
    start: Coord,
    *,
    map_path: str | Path = DEFAULT_MAP_PATH,
    scenarios_path: str | Path = DEFAULT_SCENARIOS_PATH,
    extra_crowd: list[Coord] | None = None,
    extra_smoke: list[Coord] | None = None,
    extra_fire: list[Coord] | None = None,
) -> Grid:
    scenarios = load_scenarios(scenarios_path)
    if scenario_name not in scenarios:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    grid = Grid(map_path, start=start, scenario=scenarios[scenario_name])
    grid.add_custom_hazards(
        crowd=extra_crowd or [],
        smoke=extra_smoke or [],
        fire=extra_fire or [],
    )
    return grid


def parse_coordinates(raw: str) -> list[Coord]:
    """Parse `row,col; row,col` input used by the Streamlit controls."""
    if not raw.strip():
        return []

    coordinates: list[Coord] = []
    for token in raw.split(";"):
        parts = [part.strip() for part in token.split(",")]
        if len(parts) != 2:
            raise ValueError("Use row,column pairs separated by semicolons, e.g. 0,2; 3,4")
        try:
            coordinates.append((int(parts[0]), int(parts[1])))
        except ValueError as error:
            raise ValueError("Hazard coordinates must be integers") from error
    return coordinates
