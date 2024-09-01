import numpy as np
from itertools import permutations, combinations

def shapley_value(N, v):
    players = list(N)
    n = len(players)
    factorial = np.math.factorial

    def marginal_contribution(S, i):
        S_with_i = tuple(sorted(S + (i,)))
        S_without_i = tuple(sorted(S))
        return v.get(S_with_i, 0) - v.get(S_without_i, 0)

    shapley_values = {i: 0 for i in players}

    for i in players:
        for S in combinations(players, len(players) - 1):
            if i not in S:
                S = tuple(sorted(S))
                weight = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
                shapley_values[i] += weight * marginal_contribution(S, i)

    return shapley_values

def calculate_all_subgame_shapley_values(N, v):
    all_shapley_values = {}
    for subset_size in range(1, len(N) + 1):
        for subset in combinations(N, subset_size):
            subset_v = {tuple(sorted(k)): v[k] for k in v if set(k).issubset(subset)}
            subset_shapley_values = shapley_value(subset, subset_v)
            all_shapley_values[tuple(sorted(subset))] = subset_shapley_values
    return all_shapley_values

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

# Calculate Shapley values for all subgames
all_shapley_values = calculate_all_subgame_shapley_values(N, v)
for subset, values in all_shapley_values.items():
    print(f"Shapley values for subset {subset}: {values}")
