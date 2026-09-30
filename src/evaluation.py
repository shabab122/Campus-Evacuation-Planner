from __future__ import annotations

import pandas as pd

from .astar import a_star
from .bfs import bfs
from .dfs import dfs
from .greedy import greedy_best_first
from .routing import plan_evacuation
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

    result = plan_evacuation(
        ALGORITHMS[name], grid,
        weighted_output=name not in {"BFS", "DFS"},
        include_trace=include_trace,
    )
    result["algorithm"] = name
    return result


def compare_algorithms(grid, *, include_trace: bool = False):
    return [
        run_algorithm(name, grid, include_trace=include_trace)
        for name in ALGORITHMS
    ]


def results_dataframe(results):
    rows = [
        {
            "Algorithm": result["algorithm"],
            "Route Found": "Yes" if result["route_found"] else "No",
            "Selected Exit": str(result["selected_exit"]) if result["selected_exit"] else "-",
            "Destination Type": (result["destination_type"] or "unavailable").replace("_", " "),
            "Selected Destination": str(result["selected_destination"]) if result["selected_destination"] is not None else "-",
            "Fallback Used": "Yes" if result["fallback_used"] else "No",
            "Route Risk": {"safe": "Safe (model)", "risky": "Risky", "unavailable": "No route"}[result["risk_level"]],
            "Smoke Cells": result["hazard_exposure"]["smoke"],
            "Crowd Cells": result["hazard_exposure"]["crowd"],
            "Path Steps": result["path_steps"],
            "Route Cost": result["route_cost"],
            "Nodes Explored": result["nodes_explored"],
            "Execution (ms)": result["execution_ms"],
        }
        for result in results
    ]
    return pd.DataFrame(rows)
