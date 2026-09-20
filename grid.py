import json



class Grid:


    def __init__(self, file_path):


        with open(file_path, "r") as file:

            data = json.load(file)



        self.rows = data["rows"]

        self.cols = data["cols"]


        self.start = tuple(
            data["start"]
        )


        self.exit = tuple(
            data["exit"]
        )


        self.grid = data["grid"]




    def is_valid_position(self, position):


        row, col = position


        return (

            0 <= row < self.rows

            and

            0 <= col < self.cols

        )




    def is_blocked(self, position):


        row, col = position


        return self.grid[row][col] == -1




    def get_neighbors(self, position):


        row, col = position


        directions = [

            (-1,0), # up

            (1,0),  # down

            (0,-1), # left

            (0,1)   # right

        ]


        neighbors = []



        for dr, dc in directions:


            new_position = (

                row + dr,

                col + dc

            )



            if (

                self.is_valid_position(new_position)

                and

                not self.is_blocked(new_position)

            ):

                neighbors.append(new_position)



        return neighbors





    def get_cost(self, position):


        row, col = position


        return self.grid[row][col]