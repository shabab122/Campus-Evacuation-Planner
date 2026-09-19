import json


class Grid:

    def __init__(self, file_path):

        with open(file_path, "r") as file:
            data = json.load(file)

        self.rows = data["rows"]
        self.cols = data["cols"]

        self.start = tuple(data["start"])
        self.exit = tuple(data["exit"])

        self.grid = data["grid"]


    def is_valid(self, position):

        row, col = position

        return (
            0 <= row < self.rows
            and
            0 <= col < self.cols
        )


    def is_blocked(self, position):

        row, col = position

        return self.grid[row][col] == -1


    def get_cost(self, position):

        row, col = position

        return self.grid[row][col]


    def get_neighbors(self, position):

        row, col = position

        moves = [
            (-1,0),
            (1,0),
            (0,-1),
            (0,1)
        ]

        neighbors = []


        for dr, dc in moves:

            new_position = (
                row + dr,
                col + dc
            )


            if self.is_valid(new_position):

                if not self.is_blocked(new_position):

                    neighbors.append(new_position)


        return neighbors
