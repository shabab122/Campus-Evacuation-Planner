from grid import Grid


grid = Grid("../data/map.json")


print("Start:", grid.start)

print("Exit:", grid.exit)


print(
    "Neighbors of start:",
    grid.get_neighbors(grid.start)
)


print(
    "Cost of smoke zone:",
    grid.get_cost((1,4))
)
