import numpy as np
from itertools import permutations, combinations

def shapley_value(N, v):
    players = list(N)
    n = len(players)
    factorial = np.math.factorial

    def marginal_contribution(S, i):
        S_with_i = tuple(sorted(S + (i,)))
        S_without_i = tuple(sorted(S))
        return v[S_with_i] - v[S_without_i]

    shapley_values = {i: 0 for i in players}

    for i in players:
        for S in combinations(players, len(players) - 1):
            if i not in S:
                S = tuple(sorted(S))
                weight = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
                shapley_values[i] += weight * marginal_contribution(S, i)

    return shapley_values

# Define the game
N = {'P1', 'P2', 'P3', 'P4'}
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

# Convert to tuples for consistency
v = {tuple(sorted(k)): v[k] for k in v}

# Calculate Shapely values
shapley_values = shapley_value(N, v)
print(shapley_values)
