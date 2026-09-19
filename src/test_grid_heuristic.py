from grid import Grid
from heuristic import manhattan_distance



grid = Grid("../data/map.json")



distance = manhattan_distance(
    grid.start,
    grid.exit
)



print("Start:", grid.start)

print("Exit:", grid.exit)

print("Estimated distance:", distance)
