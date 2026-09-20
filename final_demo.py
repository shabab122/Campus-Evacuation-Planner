from src.grid import Grid
from src.bfs import bfs
from src.astar import a_star
from src.visualization import draw_grid


def print_line():
    print("=" * 40)



def main():

    print_line()

    print(" Campus Evacuation Planner Demo ")

    print_line()


    # Load map

    grid = Grid("data/map.json")



    print("\n========== BFS ==========")


    bfs_path, bfs_explored = bfs(grid)



    if bfs_path:

        print(
            "Path Length:",
            len(bfs_path)
        )

        print(
            "Explored Nodes:",
            bfs_explored
        )

    else:

        print("No BFS path found")




    print("\n========== A* ==========")


    astar_path, astar_cost, astar_explored = a_star(grid)



    if astar_path:


        print(
            "Path Cost:",
            astar_cost
        )


        print(
            "Path Length:",
            len(astar_path)
        )


        print(
            "Explored Nodes:",
            astar_explored
        )


    else:

        print("No A* path found")




    print("\nOpening Visualization...")


    draw_grid(
        grid,
        astar_path
    )



if __name__ == "__main__":

    main()
