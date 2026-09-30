import json

import pytest

from src.grid import Grid
from src.scenarios import DEFAULT_MAP_PATH, build_grid, load_locations, parse_coordinates


@pytest.mark.parametrize("field", ["extra_fire", "extra_blocked", "extra_smoke", "extra_crowd"])
def test_start_cell_cannot_be_overwritten_by_custom_hazard(field):
    with pytest.raises(ValueError, match="Start"):
        build_grid("Normal conditions", load_locations()["Room A"], **{field: [(0, 0)]})


@pytest.mark.parametrize("position", [(-1, 0), (0, 6), (1, 1), (1.5, 2), (True, 2), (2,)])
def test_invalid_hazard_coordinates_are_rejected(position):
    with pytest.raises(ValueError):
        build_grid("Normal conditions", load_locations()["Room A"], extra_fire=[position])


@pytest.mark.parametrize("change", [
    {"central_stairs": [3, 3]},
    {"central_stairs": [7, 2]},
    {"central_stairs": [0, 5]},
    {"exits": []},
])
def test_invalid_stair_or_exit_configuration_is_rejected(change, tmp_path):
    data = json.loads(DEFAULT_MAP_PATH.read_text(encoding="utf-8"))
    data.update(change)
    path = tmp_path / "invalid-map.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        Grid(path)


def test_switching_scenarios_removes_old_exit_and_stair_fire():
    grid = build_grid("No traversable destination", load_locations()["Room A"])
    grid.apply_scenario({})
    assert not grid.is_blocked(grid.central_stairs)
    assert all(not grid.is_blocked(exit_) for exit_ in grid.exits)
    assert grid.hazards == {}


@pytest.mark.parametrize("raw", ["0,2;", "x,2", "1,2,3"])
def test_malformed_sidebar_coordinate_text_is_rejected(raw):
    with pytest.raises(ValueError):
        parse_coordinates(raw)
