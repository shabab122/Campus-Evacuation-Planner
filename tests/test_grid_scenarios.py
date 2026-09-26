from src.scenarios import build_grid, load_locations


def test_smoke_and_crowd_change_movement_costs():
    locations = load_locations()
    grid = build_grid("Smoke near north exit", locations["Room A"])
    assert grid.get_cost((0, 1)) == 3
    assert grid.get_cost((0, 2)) == 8
    assert len(grid.exits) == 2


def test_fire_cell_is_blocked():
    locations = load_locations()
    grid = build_grid("North corridor blocked", locations["Room A"])
    assert grid.is_blocked((0, 3))
