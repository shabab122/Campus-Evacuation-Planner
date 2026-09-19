def calculate_path_cost(grid, path):

    total_cost = 0


    for position in path:

        # Start position has no movement cost
        if position == grid.start:
            continue


        total_cost += grid.get_cost(position)


    return total_cost
