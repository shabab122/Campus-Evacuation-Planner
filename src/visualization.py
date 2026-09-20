import pygame
import time


CELL_SIZE = 80


# Colors

BACKGROUND = (30, 30, 40)

EMPTY = (240, 240, 240)

WALL = (45, 45, 55)

GRID = (120, 120, 120)

PATH = (50, 150, 255)

START = (40, 220, 80)

EXIT = (240, 60, 60)

TEXT = (255,255,255)



def draw_cell(screen, color, row, col):

    x = col * CELL_SIZE
    y = row * CELL_SIZE


    rect = pygame.Rect(
        x,
        y,
        CELL_SIZE,
        CELL_SIZE
    )


    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=12
    )


    pygame.draw.rect(
        screen,
        GRID,
        rect,
        2,
        border_radius=12
    )




def draw_grid(grid, path):

    pygame.init()


    width = grid.cols * CELL_SIZE
    height = grid.rows * CELL_SIZE + 80


    screen = pygame.display.set_mode(
        (width,height)
    )


    pygame.display.set_caption(
        "Campus Emergency Evacuation Planner"
    )


    font = pygame.font.SysFont(
        "Arial",
        24
    )


    clock = pygame.time.Clock()


    running=True



    path_index = 0



    while running:


        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running=False



        screen.fill(BACKGROUND)



        # Draw map

        for r in range(grid.rows):

            for c in range(grid.cols):


                if grid.grid[r][c] == -1:

                    color=WALL

                else:

                    color=EMPTY



                draw_cell(
                    screen,
                    color,
                    r,
                    c
                )



        # Animated path

        if path:

            for r,c in path[:path_index]:

                draw_cell(
                    screen,
                    PATH,
                    r,
                    c
                )


            if path_index < len(path):

                path_index += 1

                time.sleep(0.15)



        # Start

        draw_cell(
            screen,
            START,
            grid.start[0],
            grid.start[1]
        )



        # Exit

        draw_cell(
            screen,
            EXIT,
            grid.exit[0],
            grid.exit[1]
        )



        # Legend

        legend1 = font.render(
            "Green: Start     Red: Exit",
            True,
            TEXT
        )


        legend2 = font.render(
            "Blue: Route      Black: Wall",
            True,
            TEXT
        )


        screen.blit(
            legend1,
            (20, grid.rows*CELL_SIZE+10)
        )


        screen.blit(
            legend2,
            (20, grid.rows*CELL_SIZE+40)
        )



        pygame.display.update()


        clock.tick(60)



    pygame.quit()
