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

class Cell:
    def __init__(self, row, col, size, alive_colour, dead_colour):
        self.row = row
        self.col = col
        self.size = size
        self.alive_colour = alive_colour
        self.dead_colour = dead_colour
        self.state = 0
    
    def change_state(self):
        self.state = 1 - self.state
    
    def set_alive(self):
        self.state = 1
    def set_dead(self):
        self.state = 0

    def colour(self, screen):
        colour = self.alive_colour if self.state == 1 else self.dead_colour
        pg.draw.rect(screen, colour, (self.col * self.size, self.row * self.size, self.size - 1, self.size - 1))

class Grid:
    def __init__(self, rows, cols, size, alive_colour, dead_colour):
        self.rows = rows
        self.cols = cols
        self.size = size
        self.alive_colour = alive_colour
        self.dead_colour = dead_colour
        
        self.cells = np.empty((rows, cols), dtype=object)
        for row in range(rows):
            for col in range(cols):
                self.cells[row, col] = Cell(row, col, size, alive_colour, dead_colour)

    def update(self):
        new_grid = np.empty((self.rows, self.cols), dtype=object)
        for row in range(self.rows):
            for col in range(self.cols):
                new_grid[row, col] = Cell(row, col, self.size, self.alive_colour, self.dead_colour)
                new_grid[row, col].state = self.cells[row, col].state
                neighbours = self.sum_neighbours(row, col)
                if self.cells[row, col].state == 1:
                    if neighbours < 2 or neighbours > 3:
                        new_grid[row, col].set_dead()
                else:
                    if neighbours == 3:
                        new_grid[row, col].set_alive()
        self.cells = new_grid

    def sum_neighbours(self, i, j):
        a = max(0, i - 1)
        b = min(self.rows, i + 2)
        c = max(0, j - 1)
        d = min(self.cols, j + 2)
        submatrix = self.cells[a:b, c:d]
        return np.sum([cell.state for row in submatrix for cell in row]) - self.cells[i, j].state
    
    def clear(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.cells[row, col] = Cell(row, col, self.size, self.alive_colour, self.dead_colour)

    def draw_grid(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                self.cells[row, col].colour(screen)

class GameOfLife:
    def __init__(self, width, height, cell_size):
        pg.init()
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption("Cellular Automata: Conway's Game of Life")
        self.clock = pg.time.Clock()

        self.alive_color = (30, 200, 0)
        self.dead_color = (30, 30, 30)
        self.grid = Grid(width // cell_size, height // cell_size, cell_size, self.alive_color, self.dead_color)

        self.interval = 10
        self.paused = True
                    
    def run(self):
        running = True

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                    elif event.key == pg.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pg.K_r:
                        self.grid.clear()
                        self.paused = True
                # User drawing
                if event.type == pg.MOUSEBUTTONDOWN and self.paused:
                    if event.button == 1: 
                        x, y = pg.mouse.get_pos()
                        col, row = x // self.grid.size, y // self.grid.size
                        self.grid.cells[row, col].change_state()
                # Holding down the mouse to draw
                if event.type == pg.MOUSEMOTION and self.paused:
                    if pg.mouse.get_pressed()[0]:  
                        x, y = pg.mouse.get_pos()
                        col, row = x // self.grid.size, y // self.grid.size
                        self.grid.cells[row, col].set_alive()

            if not self.paused:
                self.grid.update()

            self.screen.fill((0, 0, 0))
            self.grid.draw_grid(self.screen)
            pg.display.flip()
            self.clock.tick(self.interval)
            
        pg.quit()

if __name__ == "__main__":
    game = GameOfLife(800, 800, 15)
    game.run()









''' functional programming version pre-oop refractor

# Grid size
n = 800
alive_colour = (30,200,0)
dead_colour = (30,30,30)
cell_size = 15
interval = 10

rows = n // 15
cols = n // 15


# py game initial setup
pg.init()
screen = pg.display.set_mode((n,n))
pg.display.set_caption("Cellular Automata: Conways's Game of Life")
clock = pg.time.Clock()
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
    # max(0, i-1), min(rows-1, i+2)
    # max(0, j-1), min(columns-1, j+2)

    submatrix = grid[max(0, i-1):min(rows, i+2), max(0, j-1):min(cols, j+2)]
    return np.sum(submatrix) - grid[i,j]


# Update grid
def update_grid():
    global grid
    new_grid = np.copy(grid)
    for row in range(rows):
        for col in range(cols):
            # sum of alive neighbours > 3 to birth 
            # sum of alive neighbours > 2 survival of alive cell  
            neighbours = sumNeighbours(row,col)
            if new_grid[row,col] == 1:
                # Over/underpopulation
                if neighbours < 2 or neighbours > 3:
                    new_grid[row,col] = 0
            # birth condition, otherwise keep as alive
            else:
                if neighbours == 3:
                    new_grid[row,col] = 1
    grid = new_grid
                      


def main():
    global grid
    
    screen.fill((0,0,0))

    running = True
    paused = True

    while running:

        for event in pg.event.get():
            # Quit conditions
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                # pause or unpause
                elif event.key == pg.K_SPACE:
                    paused = not paused
                # Reset board and pause TODO: Fix
                elif event.key == pg.K_r:
                    grid = np.zeros((n//cell_size,n//cell_size), dtype=int)
                    paused = True
            # User drawing
            if event.type == pg.MOUSEBUTTONDOWN and paused:
                if event.button == 1: 
                    x, y = pg.mouse.get_pos()
                    col, row = x // cell_size, y // cell_size
                    grid[row,col] = 1 - grid[row,col]
            # Holding down the mouse to draw
            if event.type == pg.MOUSEMOTION:
                if pg.mouse.get_pressed()[0]:  
                    x, y = pg.mouse.get_pos()
                    col, row = x // cell_size, y // cell_size
                    grid[row, col] = 1

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

'''
