from grid import Grid



grid = Grid("../data/map.json")



print("Rows:", grid.rows)

print("Columns:", grid.cols)


print("Start:", grid.start)

print("Exit:", grid.exit)



print("\nNeighbours of start:")


print(
    grid.get_neighbors(
        grid.start
    )
)


print(
    "\nCost:",
    grid.get_cost((0,1))
)