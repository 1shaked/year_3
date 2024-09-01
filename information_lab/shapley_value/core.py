from itertools import combinations
import numpy as np

def calculate_core(N, v):
    """
    Calculate the core of a cooperative game.

    Parameters:
    N (set): Set of players
    v (dict): Characteristic function that maps subsets of N to their value

    Returns:
    list: List of allocations in the core (if any)
    """
    players = list(N)
    n = len(players)
    
    # Initialize a list to store core allocations
    core_allocations = []

    # Check all possible allocations that sum up to v(N)
    allocations = list(generate_allocations(players, v[tuple(players)]))
    for allocation in allocations:
        # Check coalitional rationality for every coalition
        if all(sum(allocation[player] for player in coalition) >= v[tuple(sorted(coalition))] 
               for r in range(1, n+1) for coalition in combinations(players, r)):
            core_allocations.append(allocation)
    
    return core_allocations

def generate_allocations(players, total_value):
    """
    Generate all possible allocations of the total value among players.

    Parameters:
    players (list): List of players
    total_value (float): Total value to be allocated

    Yields:
    dict: Possible allocation among players
    """
    n = len(players)
    # Iterate over all possible allocations
    for alloc in np.linspace(0, total_value, num=11):  # Example with steps of 0.1
        if n == 1:
            yield {players[0]: total_value}
        else:
            for sub_allocation in generate_allocations(players[1:], total_value - alloc):
                allocation = {players[0]: alloc}
                allocation.update(sub_allocation)
                yield allocation

# Example usage
N = {'p1', 'p2'}
v = {(): 0, ('p1',): 1, ('p2',): 2, ('p1', 'p2'): 4}
core = calculate_core(N, v)
print("Core allocations:", core)
