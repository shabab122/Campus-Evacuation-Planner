from src.astar import a_star
from src.evaluation import compare_algorithms
from src.scenarios import build_grid, load_locations
from src.ucs import ucs


def test_astar_matches_ucs_weighted_cost():
    locations = load_locations()
    grid = build_grid("Smoke near north exit", locations["Room A"])
    _, astar_cost, _ = a_star(grid)
    _, ucs_cost, _ = ucs(grid)
    assert astar_cost == ucs_cost


def test_all_five_algorithms_are_compared():
    locations = load_locations()
    grid = build_grid("Normal conditions", locations["Room A"])
    results = compare_algorithms(grid)
    assert {result["algorithm"] for result in results} == {
        "A*",
        "BFS",
        "DFS",
        "UCS",
        "Greedy Best First",
    }
    assert all("execution_ms" in result for result in results)
