import heapq

from heuristic import manhattan_distance


def a_star(grid):

    start = grid.start
    goal = grid.exit


    # Priority Queue
    # Format: (f_score, node)
    open_set = []

    heapq.heappush(
        open_set,
        (0, start)
    )


    # Store parent node
    came_from = {}


    # g(n) cost from start
    g_score = {

        start: 0

    }


    # Count explored nodes
    explored_nodes = 0



    while open_set:


        # Node with lowest f(n)
        current = heapq.heappop(open_set)[1]


        explored_nodes += 1



        # Goal reached
        if current == goal:


            path = reconstruct_path(
                came_from,
                current
            )


            total_cost = g_score[current]


            return (
                path,
                total_cost,
                explored_nodes
            )



        # Explore neighbours

        for neighbor in grid.get_neighbors(current):


            # Calculate new g(n)

            movement_cost = grid.get_cost(neighbor)


            new_cost = (

                g_score[current]

                +

                movement_cost

            )



            # If this path is better

            if (

                neighbor not in g_score

                or

                new_cost < g_score[neighbor]

            ):


                # Update cost

                g_score[neighbor] = new_cost



                # Calculate f(n)

                h_score = manhattan_distance(

                    neighbor,

                    goal

                )


                f_score = (

                    new_cost

                    +

                    h_score

                )



                # Add to priority queue

                heapq.heappush(

                    open_set,

                    (

                        f_score,

                        neighbor

                    )

                )



                # Store parent

                came_from[neighbor] = current



    # No route found

    return (
        None,
        None,
        explored_nodes
    )





def reconstruct_path(came_from, current):


    path = [current]


    while current in came_from:


        current = came_from[current]

        path.append(current)



    path.reverse()


    return path
