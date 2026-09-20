from collections import deque



def bfs(grid):

    start = grid.start
    goal = grid.exit


    queue = deque()

    queue.append(start)


    visited = set()

    visited.add(start)


    came_from = {}


    explored_nodes = 0



    while queue:


        current = queue.popleft()

        explored_nodes += 1



        # Goal found

        if current == goal:


            path = reconstruct_path(
                came_from,
                current
            )


            return (
                path,
                explored_nodes
            )



        # Check neighbours

        for neighbor in grid.get_neighbors(current):


            if neighbor not in visited:


                visited.add(neighbor)


                queue.append(neighbor)


                came_from[neighbor] = current



    return (
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
