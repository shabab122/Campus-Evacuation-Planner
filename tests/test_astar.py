from grid import Grid

from astar import a_star



grid = Grid("../data/map.json")



path, cost, explored = a_star(grid)



if path:


    print("Route Found\n")


    print("Path:")


    for step in path:

        print(step)



    print("\nTotal Cost:", cost)


    print(
        "Path Length:",
        len(path)
    )


    print(
        "Explored Nodes:",
        explored
    )


else:

    print("No path found")
