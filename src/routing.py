"""Shared two-stage destination policy; the five search algorithms stay unchanged.

Search all traversable emergency exits first. Only if that search fails, search
the central staircase from the original start on the same hazard map. Search
expansions are planning activity, not physical movement toward a blocked exit.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter

from .cost import calculate_path_cost
from .grid import Coord, Grid


@dataclass(frozen=True)
class SearchGrid:
    """Read-only target view compatible with the existing algorithm interfaces."""

    source: Grid
    exits: tuple[Coord, ...]

    @property
    def start(self) -> Coord:
        return self.source.start

    def get_neighbors(self, position: Coord) -> list[Coord]:
        return self.source.get_neighbors(position)

    def get_cost(self, position: Coord) -> int:
        return self.source.get_cost(position)


def _search_stage(
    search: Callable,
    grid: Grid,
    goals: list[Coord],
    phase: str,
    *,
    weighted_output: bool,
    include_trace: bool,
) -> dict:
    started = perf_counter()
    path, cost, explored, trace = None, None, 0, []
    # A*/Greedy require at least one goal for their heuristic. Blocked goals
    # never enter the target view; no algorithm can step into fire or a wall.
    if goals:
        output = search(SearchGrid(grid, tuple(goals)), return_trace=include_trace)
        if weighted_output:
            path, cost, explored = output[:3]
            if include_trace:
                trace = output[3]
        else:
            path, explored = output[:2]
            cost = calculate_path_cost(grid, path)
            if include_trace:
                trace = output[2]
    result = {
        "phase": phase,
        "goals": goals,
        "route_found": bool(path),
        "path": path or [],
        "route_cost": cost,
        "nodes_explored": explored,
        "execution_ms": round((perf_counter() - started) * 1000, 4),
    }
    if include_trace:
        result["exploration_order"] = trace
    return result


def plan_evacuation(
    search: Callable,
    grid: Grid,
    *,
    weighted_output: bool,
    include_trace: bool = False,
) -> dict:
    """Plan an exit-first route and report the actual route's hazard exposure.

    Smoke/crowd remain traversable. Their presence is reported as risk, including
    on a destination cell. No-path results remain valid when the fallback is
    absent, blocked, or unreachable; a route is never fabricated.
    """
    started = perf_counter()
    blocked_exits = [position for position in grid.exits if grid.is_blocked(position)]
    exit_goals = [position for position in grid.exits if position not in blocked_exits]
    primary = _search_stage(
        search, grid, exit_goals, "emergency_exits",
        weighted_output=weighted_output, include_trace=include_trace,
    )
    stages = [primary]
    selected = primary
    fallback_used = not primary["route_found"]
    if fallback_used and grid.central_stairs is not None:
        stairs_goals = [] if grid.is_blocked(grid.central_stairs) else [grid.central_stairs]
        selected = _search_stage(
            search, grid, stairs_goals, "central_stairs",
            weighted_output=weighted_output, include_trace=include_trace,
        )
        stages.append(selected)

    path = selected["path"]
    destination = path[-1] if path else None
    destination_type = (
        "central_stairs" if fallback_used else "emergency_exit"
    ) if path else None
    exposure = {"smoke": 0, "crowd": 0, "elevated_cost": 0}
    risk_cells = []
    for position in path:
        hazard = grid.hazard_type(position)
        label = hazard if hazard in {"smoke", "crowd"} else "elevated_cost"
        if hazard in {"smoke", "crowd"} or grid.get_cost(position) > 1:
            exposure[label] += 1
            risk_cells.append(position)
    risk_level = "unavailable" if not path else ("risky" if risk_cells else "safe")
    risk_reasons = [
        f"{count} {label.replace('_', '-')} cell(s)"
        for label, count in exposure.items() if count
    ]

    if destination_type == "central_stairs":
        message = "All emergency exits are unreachable. Route to central stairs found."
    elif destination_type == "emergency_exit":
        message = "Route to an emergency exit found."
    elif grid.central_stairs is None:
        message = "No emergency exit is reachable; central stairs are not configured."
    elif grid.is_blocked(grid.central_stairs):
        message = "No traversable route: emergency exits are unreachable and central stairs are fire/blocked."
    else:
        message = "No traversable route: emergency exits and central stairs are unreachable."
    if risk_level == "risky":
        message += " Risk warning: " + ", ".join(risk_reasons) + "."

    result = {
        "route_found": bool(path),
        # Retain the old field without mislabelling stairs as an emergency exit.
        "selected_exit": destination if destination_type == "emergency_exit" else None,
        "selected_destination": destination,
        "destination_type": destination_type,
        "fallback_used": fallback_used,
        "stairs_visible": fallback_used and grid.central_stairs is not None,
        "blocked_exits": blocked_exits,
        "path": path,
        "path_steps": max(len(path) - 1, 0),
        "route_cost": selected["route_cost"],
        # These totals include the failed primary search and the fallback search.
        "nodes_explored": sum(stage["nodes_explored"] for stage in stages),
        "execution_ms": round((perf_counter() - started) * 1000, 4),
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "hazard_exposure": exposure,
        "risk_cells": risk_cells,
        "message": message,
        "stages": stages,
    }
    if include_trace:
        result["exploration_order"] = [
            node for stage in stages for node in stage["exploration_order"]
        ]
    return result
