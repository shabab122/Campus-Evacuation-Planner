import matplotlib

matplotlib.use("Agg")

from src.evaluation import ALGORITHMS, run_algorithm
from src.scenarios import build_grid, load_locations
from src.visualization import draw_grid


def test_algorithm_trace_matches_explored_count():
    locations = load_locations()
    grid = build_grid("Smoke near north exit", locations["Room A"])

    for name in ALGORITHMS:
        result = run_algorithm(name, grid, include_trace=True)
        assert result["route_found"] is True
        assert len(result["exploration_order"]) == result["nodes_explored"]
        assert result["exploration_order"][0] == grid.start
        assert result["path"][0] == grid.start
        assert result["path"][-1] in grid.exits


def test_visualizer_accepts_live_search_and_traveler_layers():
    locations = load_locations()
    grid = build_grid("Normal conditions", locations["Room A"])
    result = run_algorithm("A*", grid, include_trace=True)

    figure = draw_grid(
        grid,
        path=result["path"],
        explored=result["exploration_order"],
        current=result["exploration_order"][-1],
        traveler=result["path"][-1],
        title="Test frame",
    )
    assert figure.axes
