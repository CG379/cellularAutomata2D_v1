# Conway's Game of Life: Only input allowed
''' 
Rules:
    Any live cell with fewer than two live neighbors dies, as if by underpopulation.
    Any live cell with two or three live neighbors lives on to the next generation.
    Any live cell with more than three live neighbors dies, as if by overpopulation.
    Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.

People turn these into codes for easy input:
B3/S23  birth of a cell needs 3 neighbours, survival of a cell needs 2 or 3 neighbours 
'''

import numpy as np
import pygame as pg

# Grid size
n = 800
alive_colour = (30,200,0)
dead_colour = (30,30,30)
cell_size = 15
interval = 10

rows = n // 15
cols = n // 15

grid =  np.zeros((n//cell_size,n//cell_size), dtype=int)



# Draw grid
def draw_grid(screen):
    for row in range(rows):
        for col in range(cols):
            if grid[row,col] == 1:
                colour = alive_colour
            else:
                colour = dead_colour
            # (sceen, color, (x,y,width,height))
            pg.draw.rect(screen, colour,(col * cell_size, row * cell_size, cell_size - 1, cell_size - 1))

# Neighbour sum
def sumNeighbours(i,j):
    ###
    # # 
    ### 
    # max(0, i-1), min(rows-1, i+1)
    # max(0, j-1), min(columns-1, j+1)
    submatrix = grid[max(0, i-1) : min(rows-1, i+1), max(0, j-1) : min(cols-1, j+1)]
    return np.sum(submatrix) - grid[i,j]


# Update grid
def update_grid():
    for row in range(rows):
        for col in range(cols):
            # sum of alive neighbours > 3 to birth 
            # sum of alive neighbours > 2 survival of alive cell  
            neighbours = sumNeighbours(row,col)
            if grid[row,col] == 1:
                # Over/underpopulation
                if neighbours < 2 or neighbours > 3:
                    grid[row,col] = 0
            # birth condition, other wise keep as alive
            else:
                if neighbours == 3:
                    grid[row,col] = 1

                      


def main():
    global grid
    # py game initial setup
    pg.init()
    screen = pg.display.set_mode((n,n))
    pg.display.set_caption("Cellular Automata: Conways's Game of Life")
    clock = pg.time.Clock()

    running = True
    paused = False

    while running:

        for event in pg.event.get():
            # Quit conditions
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                # Start if paused
                elif event.key  == pg.K_SPACE and paused:
                    paused = False
                # Pause if start
                elif event.type == pg.K_SPACE:
                    paused = True
                # Reset board and pause
                elif event.type == pg.K_r:
                    paused = True
                    grid = np.zeros((n//cell_size,n//cell_size), dtype=int)
            # User drawing
            # Left button pressed
            if pg.mouse.get_pressed()[0]: 
                x, y = pg.mouse.get_pos()
                col, row = x // cell_size, y // cell_size
                grid[row, col] = 1 - grid[row, col]
            
            # Update grid for user
            if paused == False:
                update_grid()
            
            

                
        screen.fill((0,0,0))
        draw_grid(screen)
        pg.display.flip()
        clock.tick(interval)


    pg.quit()

if __name__ == "__main__":
    main()
