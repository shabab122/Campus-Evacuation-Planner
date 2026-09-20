from grid import Grid
from bfs import bfs



grid = Grid("../data/map.json")



path, explored = bfs(grid)



if path:


    print("BFS Route Found\n")


    print("Path:")


    for node in path:

        print(node)



    print(
        "\nPath Length:",
        len(path)
    )


    print(
        "Explored Nodes:",
        explored
    )


else:

    print("No Path Found")
