import pygame


CELL_SIZE = 60


NORMAL = (220, 220, 220)
WALL = (0, 0, 0)
START = (0, 255, 0)
EXIT = (255, 0, 0)
PATH = (0, 0, 255)
GRID_LINE = (100, 100, 100)


def draw_grid(grid, path):

    pygame.init()

    width = grid.cols * CELL_SIZE
    height = grid.rows * CELL_SIZE

    screen = pygame.display.set_mode(
        (width, height)
    )

    pygame.display.set_caption(
        "Campus Emergency Evacuation Planner"
    )

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False


        screen.fill((255,255,255))


        for row in range(grid.rows):

            for col in range(grid.cols):

                x = col * CELL_SIZE
                y = row * CELL_SIZE


                rect = pygame.Rect(
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                )


                value = grid.grid[row][col]


                color = NORMAL


                if value == -1:
                    color = WALL


                if (row, col) == grid.start:
                    color = START


                elif (row, col) == grid.exit:
                    color = EXIT



                pygame.draw.rect(
                    screen,
                    color,
                    rect
                )


                pygame.draw.rect(
                    screen,
                    GRID_LINE,
                    rect,
                    1
                )


        # Draw path

        if path:

            for row, col in path:

                pygame.draw.rect(
                    screen,
                    PATH,
                    (
                        col * CELL_SIZE,
                        row * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                )


        pygame.display.update()


    pygame.quit()