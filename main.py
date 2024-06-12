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
n = 100


# Build empty canvas
def build_empty_grid(size):
    return np.zeros((size,size))



# Draw shape

# Update grid

# Execute pattern
# Pause function


def main():
    pg.init()
    screen = pg.display.set_mode((n,n))
    pg.display.set_caption("Cellular Automata: Conways's Game of Life")
    pg.mouse.set_visible(True)
    running = True
    pause = False

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.K_SPACE:
                pause = True



    pg.quit()

main()


