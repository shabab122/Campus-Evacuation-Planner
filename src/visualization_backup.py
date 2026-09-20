import pygame


# =========================
# Configuration
# =========================

CELL_SIZE = 80

WIDTH_PADDING = 20


# Colors

WHITE = (240, 240, 240)
BLACK = (0, 0, 0)

GREEN = (0, 200, 0)
RED = (220, 0, 0)

BLUE = (50, 100, 255)

GRAY = (120, 120, 120)

YELLOW = (255, 220, 0)



# =========================
# Draw Grid
# =========================

def draw_grid(grid, path):

    pygame.init()


    screen_width = grid.cols * CELL_SIZE
    screen_height = grid.rows * CELL_SIZE


    screen = pygame.display.set_mode(
        (
            screen_width,
            screen_height
        )
    )


    pygame.display.set_caption(
        "Campus Evacuation Planner"
    )



    clock = pygame.time.Clock()


    running = True



    while running:


        # ---------------------
        # Event Handling
        # ---------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False



        screen.fill(WHITE)



        # ---------------------
        # Draw Cells
        # ---------------------

        for row in range(grid.rows):

            for col in range(grid.cols):


                rect = pygame.Rect(

                    col * CELL_SIZE,

                    row * CELL_SIZE,

                    CELL_SIZE,

                    CELL_SIZE

                )


                cell_value = grid.grid[row][col]



                # Wall

                if cell_value == -1:

                    color = BLACK


                else:

                    color = WHITE



                pygame.draw.rect(

                    screen,

                    color,

                    rect

                )



                # Grid border

                pygame.draw.rect(

                    screen,

                    GRAY,

                    rect,

                    2

                )



        # ---------------------
        # Draw Path
        # ---------------------

        if path:


            for position in path:


                row, col = position



                rect = pygame.Rect(

                    col * CELL_SIZE,

                    row * CELL_SIZE,

                    CELL_SIZE,

                    CELL_SIZE

                )


                # Path highlight

                pygame.draw.rect(

                    screen,

                    BLUE,

                    rect.inflate(
                        -20,
                        -20
                    )

                )



        # ---------------------
        # Draw Start
        # ---------------------

        start_row, start_col = grid.start


        start_rect = pygame.Rect(

            start_col * CELL_SIZE,

            start_row * CELL_SIZE,

            CELL_SIZE,

            CELL_SIZE

        )


        pygame.draw.rect(

            screen,

            GREEN,

            start_rect.inflate(
                -15,
                -15
            )

        )



        # ---------------------
        # Draw Exit
        # ---------------------

        exit_row, exit_col = grid.exit


        exit_rect = pygame.Rect(

            exit_col * CELL_SIZE,

            exit_row * CELL_SIZE,

            CELL_SIZE,

            CELL_SIZE

        )


        pygame.draw.rect(

            screen,

            RED,

            exit_rect.inflate(
                -15,
                -15
            )

        )



        pygame.display.update()



        clock.tick(60)



    pygame.quit()