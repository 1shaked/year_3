# You may need to install the library first
# pip install GameTheory

from GameTheory import Game

# Define the game
v = {
    (): 0,
    ('P1',): 1,
    ('P2',): 2,
    ('P3',): 1,
    ('P4',): 1,
    ('P1', 'P2'): 3,
    ('P1', 'P3'): 2,
    ('P1', 'P4'): 2,
    ('P2', 'P3'): 3,
    ('P2', 'P4'): 3,
    ('P3', 'P4'): 2,
    ('P1', 'P2', 'P3'): 4,
    ('P1', 'P2', 'P4'): 3,
    ('P1', 'P3', 'P4'): 3,
    ('P2', 'P3', 'P4'): 4,
    ('P1', 'P2', 'P3', 'P4'): 5
}

# Create game instance
game = Game(v)

# Calculate Shapley values
shapley_values = game.shapley()
print(shapley_values)
