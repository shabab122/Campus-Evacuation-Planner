from __future__ import annotations

from time import perf_counter

import pandas as pd

from .astar import a_star
from .bfs import bfs
from .cost import calculate_path_cost
from .dfs import dfs
from .greedy import greedy_best_first
from .ucs import ucs


ALGORITHMS = {
    "A*": a_star,
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "Greedy Best First": greedy_best_first,
}


def run_algorithm(name, grid, *, include_trace: bool = False):
    """Run one algorithm and normalize its metrics for the UI.

    ``include_trace=True`` returns the exact node-expansion order used by the
    live Streamlit visualization. Comparison-only runs may omit it.
    """
    if name not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {name}")

    started = perf_counter()
    output = ALGORITHMS[name](grid, return_trace=include_trace)
    duration_ms = (perf_counter() - started) * 1000

    if name in {"BFS", "DFS"}:
        if include_trace:
            path, explored, exploration_order = output
        else:
            path, explored = output
            exploration_order = []
        cost = calculate_path_cost(grid, path)
    else:
        if include_trace:
            path, cost, explored, exploration_order = output
        else:
            path, cost, explored = output
            exploration_order = []

    normalized_path = path or []
    selected_exit = normalized_path[-1] if normalized_path else None
    result = {
        "algorithm": name,
        "route_found": bool(normalized_path),
        "selected_exit": selected_exit,
        "path": normalized_path,
        "path_steps": max(len(normalized_path) - 1, 0),
        "route_cost": cost,
        "nodes_explored": explored,
        "execution_ms": round(duration_ms, 4),
    }
    if include_trace:
        result["exploration_order"] = exploration_order
    return result


def compare_algorithms(grid, *, include_trace: bool = False):
    return [
        run_algorithm(name, grid, include_trace=include_trace)
        for name in ALGORITHMS
    ]
