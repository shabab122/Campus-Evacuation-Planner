"""Behavior tests for destination priority, unreachable goals, and route risk."""

import json
from collections import deque

import pytest

from src.cost import calculate_path_cost
from src.evaluation import ALGORITHMS, results_dataframe, run_algorithm
from src.grid import Grid
from src.scenarios import DEFAULT_MAP_PATH, build_grid, load_locations, load_scenarios


NAMES = list(ALGORITHMS)
LOCATIONS = load_locations()


def start_has_hazard(scenario, location):
    hazards = load_scenarios()[scenario]
    return any(
        LOCATIONS[location] == tuple(position)
        for label in ("crowd", "smoke", "fire", "blocked")
        for position in hazards.get(label, [])
    )


def reachable_cells(grid):
    """Independent flood-fill oracle, without using the search implementations."""
    found = {grid.start}
    queue = deque([grid.start])
    while queue:
        row, col = queue.popleft()
        for neighbor in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
            if not (0 <= neighbor[0] < grid.rows and 0 <= neighbor[1] < grid.cols):
                continue
            if grid.grid[neighbor[0]][neighbor[1]] in {-1, -2} or neighbor in found:
                continue
            found.add(neighbor)
            queue.append(neighbor)
    return found


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("scenario", list(load_scenarios()))
@pytest.mark.parametrize("location", list(LOCATIONS))
def test_destination_and_path_agree_with_independent_reachability(name, scenario, location):
    if start_has_hazard(scenario, location):
        with pytest.raises(ValueError, match="Start"):
            build_grid(scenario, LOCATIONS[location])
        return
    grid = build_grid(scenario, LOCATIONS[location])
    original_exits = grid.exits.copy()
    original_cells = [row.copy() for row in grid.grid]
    reachable = reachable_cells(grid)
    exits_reachable = bool(set(grid.exits) & reachable)
    stairs_reachable = grid.central_stairs in reachable
    result = run_algorithm(name, grid, include_trace=True)

    assert result["fallback_used"] is (not exits_reachable)
    assert result["stairs_visible"] is (not exits_reachable)
    assert result["route_found"] is (exits_reachable or stairs_reachable)
    assert grid.exits == original_exits and grid.grid == original_cells
    assert result["nodes_explored"] == len(result["exploration_order"])
    assert result["nodes_explored"] == sum(stage["nodes_explored"] for stage in result["stages"])
    for stage in result["stages"]:
        assert len(stage["exploration_order"]) == stage["nodes_explored"]
        if stage["exploration_order"]:
            assert stage["exploration_order"][0] == grid.start
        assert all(not grid.is_blocked(node) for node in stage["exploration_order"])

    path = result["path"]
    if not path:
        assert result["route_cost"] is None and result["risk_level"] == "unavailable"
        assert result["selected_destination"] is None
        return
    assert path[0] == grid.start
    assert all(not grid.is_blocked(node) for node in path)
    for first, second in zip(path, path[1:]):
        assert abs(first[0] - second[0]) + abs(first[1] - second[1]) == 1
    assert result["route_cost"] == calculate_path_cost(grid, path)
    if exits_reachable:
        assert path[-1] in grid.exits
        assert result["destination_type"] == "emergency_exit"
        assert result["selected_exit"] == path[-1]
        assert len(result["stages"]) == 1
    else:
        assert path[-1] == grid.central_stairs
        assert result["destination_type"] == "central_stairs"
        assert result["selected_exit"] is None
        assert len(result["stages"]) == 2
    assert result["selected_destination"] == path[-1]
    expected_risk = any(grid.get_cost(node) > 1 for node in path)
    assert result["risk_level"] == ("risky" if expected_risk else "safe")


@pytest.mark.parametrize("name", NAMES)
def test_one_reachable_exit_takes_priority_over_nearby_stairs(name):
    grid = build_grid("Normal conditions", LOCATIONS["Room A"], extra_fire=[(0, 5)])
    result = run_algorithm(name, grid)
    assert result["selected_exit"] == (5, 5)
    assert not result["fallback_used"] and not result["stairs_visible"]


@pytest.mark.parametrize("name", NAMES)
def test_fire_or_custom_block_on_both_exits_activates_stairs(name):
    for field in ("extra_fire", "extra_blocked"):
        grid = build_grid("Normal conditions", LOCATIONS["Room A"], **{field: [(0, 5), (5, 5)]})
        result = run_algorithm(name, grid)
        assert result["selected_destination"] == grid.central_stairs
        assert result["stages"][0]["nodes_explored"] == 0
        assert result["blocked_exits"] == grid.exits


@pytest.mark.parametrize("name", NAMES)
def test_risky_stair_destination_is_counted_and_reported(name):
    grid = build_grid("Risky stairs fallback", LOCATIONS["Room A"])
    result = run_algorithm(name, grid)
    assert result["risk_level"] == "risky"
    assert result["hazard_exposure"]["smoke"] == 1
    assert grid.central_stairs in result["risk_cells"]
    assert "Risk warning" in result["message"]


def write_map(tmp_path, data):
    path = tmp_path / "map.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.mark.parametrize("name", NAMES)
def test_stairs_can_be_clear_but_unreachable(name, tmp_path):
    data = {
        "rows": 3, "cols": 4, "start": [0, 0], "exits": [[0, 3]],
        "central_stairs": [2, 3],
        "grid": [[1, -1, 1, 1], [1, -1, -1, -1], [1, -1, 1, 1]],
    }
    result = run_algorithm(name, Grid(write_map(tmp_path, data)), include_trace=True)
    assert result["fallback_used"] and result["stairs_visible"]
    assert not result["route_found"] and result["path"] == []
    assert "unreachable" in result["message"]
    assert all(not stage["route_found"] for stage in result["stages"])


@pytest.mark.parametrize("name", NAMES)
def test_legacy_map_without_stairs_does_not_crash(name, tmp_path):
    data = json.loads(DEFAULT_MAP_PATH.read_text(encoding="utf-8"))
    del data["central_stairs"]
    grid = Grid(write_map(tmp_path, data), scenario={"fire": data["exits"]})
    result = run_algorithm(name, grid)
    assert not result["route_found"] and not result["stairs_visible"]
    assert "not configured" in result["message"]


@pytest.mark.parametrize("name", NAMES)
def test_start_at_stairs_is_a_valid_zero_step_fallback(name):
    grid = build_grid("Both emergency exits on fire", (2, 3))
    result = run_algorithm(name, grid)
    assert result["path"] == [(2, 3)]
    assert result["path_steps"] == 0 and result["route_cost"] == 0
    assert result["risk_level"] == "safe"


@pytest.mark.parametrize("name", NAMES)
def test_hazardous_exit_still_takes_priority_if_reachable(name, tmp_path):
    data = {
        "rows": 2, "cols": 3, "start": [0, 0], "exits": [[0, 2]],
        "central_stairs": [1, 0], "grid": [[1, 1, 1], [1, 1, 1]],
    }
    grid = Grid(write_map(tmp_path, data), scenario={"smoke": [[0, 2]]})
    result = run_algorithm(name, grid)
    assert result["selected_exit"] == (0, 2) and not result["fallback_used"]
    assert result["risk_level"] == "risky"


@pytest.mark.parametrize("scenario", list(load_scenarios()))
@pytest.mark.parametrize("location", list(LOCATIONS))
def test_astar_and_ucs_have_equal_cost_for_primary_or_fallback(scenario, location):
    if start_has_hazard(scenario, location):
        with pytest.raises(ValueError, match="Start"):
            build_grid(scenario, LOCATIONS[location])
        return
    grid = build_grid(scenario, LOCATIONS[location])
    astar = run_algorithm("A*", grid)
    ucs = run_algorithm("UCS", grid)
    assert astar["destination_type"] == ucs["destination_type"]
    assert astar["route_cost"] == ucs["route_cost"]


def test_csv_data_distinguishes_stairs_from_exits_and_preserves_missing_cost():
    risky = build_grid("Risky stairs fallback", LOCATIONS["Room A"])
    no_route = build_grid("No traversable destination", LOCATIONS["Room A"])
    table = results_dataframe([run_algorithm("A*", risky), run_algorithm("UCS", no_route)])
    assert table.iloc[0]["Selected Exit"] == "-"
    assert table.iloc[0]["Destination Type"] == "central stairs"
    assert table.iloc[0]["Route Risk"] == "Risky"
    assert table.iloc[1]["Route Found"] == "No"
    assert table.iloc[1]["Selected Destination"] == "-"
    assert table["Route Cost"].isna().iloc[1]
