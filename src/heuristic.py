def manhattan_distance(current, goal):

    current_row, current_col = current
    goal_row, goal_col = goal


    distance = (
        abs(current_row - goal_row)
        +
        abs(current_col - goal_col)
    )


    return distance
