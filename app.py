from src.grid import Grid
from src.astar import a_star
from src.bfs import bfs
from src.visualization import draw_grid


grid = Grid("data/map.json")


path, cost, explored = a_star(grid)


# path, explored = bfs(grid)


print("Route Cost:", cost)
print("Explored Nodes:", explored)


draw_grid(
    grid,
    path
)