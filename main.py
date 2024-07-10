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
import tensorflow as tf
from tensorflow.keras import layers


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
        pg.draw.rect(screen, colour, (self.col * self.size, self.row * self.size + 60, self.size - 1, self.size - 1))


class NeuralModel:
    def __init__(self, model_path=None):
        if model_path:
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.model = self.build_model()

    def build_model(self):
        # input = 8 neighbours + 1 cell state
        # Output layer 1 or 0 = sigmoid
        # 1-5 hidden layers adn 10-100 each, source Hands-on Machine Learning
        # Decreasing by 1/3 per layer?
        # TODO: Figure out why for hidden layers
        model = tf.keras.Sequential([
            layers.Input(shape =(9,)),
            layers.Dense(30, activation='relu'),
            layers.Dense(10, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        # Compile model
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])  
        return model

    def predict(self,input):
        return self.model.predict(input)
    
    def train(self,X,y,epochs=10):
        self.model.fit(X,y,epochs=epochs)
    
    def save_model(self, path):
        self.model.save(path)



class Grid:
    def __init__(self, rows, cols, size, alive_colour, dead_colour):
        self.rows = rows
        self.cols = cols
        self.size = size
        self.alive_colour = alive_colour
        self.dead_colour = dead_colour
        self.neural_model = NeuralModel()

        self.cells = np.empty((rows, cols), dtype=object)
        for row in range(rows):
            for col in range(cols):
                self.cells[row, col] = Cell(row, col, size, alive_colour, dead_colour)


    def update(self):
        new_grid = np.empty((self.rows, self.cols), dtype=object)
        prediction_inputs = []
        positions = []

        for row in range(self.rows):
            for col in range(self.cols):
                new_grid[row, col] = Cell(row, col, self.size, self.alive_colour, self.dead_colour)
                neighbors = self.get_neighbors(row, col)
                prediction_inputs.append(neighbors)
                positions.append((row, col))

        prediction_inputs = np.array(prediction_inputs)
        predictions = self.neural_model.predict(prediction_inputs)

        for i, (row, col) in enumerate(positions):
            new_grid[row, col].state = 1 if predictions[i, 0] > 0.5 else 0

        self.cells = new_grid

    def get_neighbors(self, row, col):
        neighbors = []
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if 0 <= i < self.rows and 0 <= j < self.cols:
                    # Add neighbor's state to the list
                    neighbors.append(self.cells[i, j].state)  
                else:
                    # Out of bounds cells are considered dead
                    neighbors.append(0)  
        return neighbors

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
        
    def randomise(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.cells[row, col].state = np.random.choice([0, 1])


class Button:
    def __init__(self, x, y, width, height, text, font, bg_color, text_color):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color

    def draw(self, screen):
        pg.draw.rect(screen, self.bg_color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class GameOfLife:
    def __init__(self, width, height, cell_size):
        # pygame setup
        pg.init()
        self.screen = pg.display.set_mode((width, height + 60))
        pg.display.set_caption("Cellular Automata: Conway's Game of Life")
        self.clock = pg.time.Clock()
        # Constants 
        self.alive_color = (30, 200, 0)
        self.dead_color = (30, 30, 30)
        self.grid = Grid(width // cell_size, height // cell_size, cell_size, self.alive_color, self.dead_color)

        self.interval = 1
        self.paused = True

        # buttons font
        self.font = pg.font.Font(None, 36)

        #buttons
        self.buttons = []
        button_texts = ['Start/Pause', 'Clear', 'Rand']
        button_width = 150
        button_height = 40
        for i, text in enumerate(button_texts):
            x_pos = (width // 4) * (i + 1) - (button_width // 2)
            self.buttons.append(Button(x_pos, 10, button_width, button_height, text, self.font, (200, 200, 200), (0, 0, 0)))

    def is_within_bounds(self, row, col):
        return 0 <= row < self.grid.rows and 0 <= col < self.grid.cols

    def handle_button_click(self, pos):
        # Button cases
        for button in self.buttons:
            if button.is_clicked(pos):
                if button.text == 'Start/Pause':
                    self.paused = not self.paused
                elif button.text == 'Clear':
                    self.grid.clear()
                    self.paused = True
                elif button.text == 'Rand':
                    self.grid.randomise()

    def run(self):
        running = True

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                # Quit condition
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos = pg.mouse.get_pos()
                    # click is below button area
                    if pos[1] > 60:  
                        col, row = pos[0] // self.grid.size, (pos[1] - 60) // self.grid.size
                        # press to draw
                        if self.is_within_bounds(row, col) and self.paused:
                            self.grid.cells[row, col].change_state()
                    else:
                        self.handle_button_click(pos)

                if event.type == pg.MOUSEMOTION and self.paused:
                    if pg.mouse.get_pressed()[0]:
                        pos = pg.mouse.get_pos()
                        # hold to draw
                        if pos[1] > 60:  
                            col, row = pos[0] // self.grid.size, (pos[1] - 60) // self.grid.size
                            if self.is_within_bounds(row, col):
                                self.grid.cells[row, col].set_alive()

            if not self.paused:
                self.grid.update()

            self.screen.fill((0, 0, 0))
            self.grid.draw_grid(self.screen)
            # Draw buttons
            for button in self.buttons:
                button.draw(self.screen)
            # Refresh screen
            pg.display.flip()
            self.clock.tick(self.interval)

        pg.quit()


def generate_training_data(grid, steps):
    X = []
    y = []
    for _ in range(steps):
        for row in range(grid.rows):
            for col in range(grid.cols):
                neighbors = grid.get_neighbors(row, col)
                X.append(neighbors)
                alive_neighbors = sum(neighbors) - grid.cells[row, col].state
                next_state = 1 if (grid.cells[row, col].state == 1 and alive_neighbors in [2, 3]) or (grid.cells[row, col].state == 0 and alive_neighbors == 3) else 0
                y.append(next_state)
        grid.update()
    return np.array(X), np.array(y)




if __name__ == "__main__":
    game = GameOfLife(800, 800, 15)
    # Generate training data
    X, y = generate_training_data(game.grid, steps=100)
    try:
        # Load the model and use it in the game
        game.grid.neural_model = NeuralModel(model_path='neural_model.h5')
    except:
        # Train and save the model
        neural_model = NeuralModel()
        neural_model.train(X, y, epochs=5)
        neural_model.save_model('neural_model.h5')
        # Load the model and use it in the game
        game.grid.neural_model = NeuralModel(model_path='neural_model.h5')
    
    game.run()
