import itertools
from scipy.optimize import linprog

# Define the characteristic function using a dictionary
characteristic_function = {
    (): 0,
    ('p1',): 1,
    ('p2',): 2,
    ('p1', 'p2'): 4,
}

def find_core(characteristic_function):
    """Find the core of the game based on the characteristic function provided."""
    players = sorted(set(player for coalition in characteristic_function for player in coalition))
    n = len(players)

    # Map each player to an index
    player_index = {player: i for i, player in enumerate(players)}
    
    # Set up the linear programming problem
    A = []  # Coefficients matrix for inequalities
    b = []  # Right-hand side of inequalities

    # Core constraints: sum(x_i for i in S) >= v(S) for all S
    for coalition, value in characteristic_function.items():
        if coalition:  # Skip the empty coalition
            constraint = [1 if player in coalition else 0 for player in players]
            A.append(constraint)
            b.append(value)

    # Efficiency constraint: sum(x_i) = v(N) where N is the grand coalition
    grand_coalition_value = characteristic_function[tuple(players)]
    A_eq = [[1] * n]
    b_eq = [grand_coalition_value]

    # Bounds for each player's allocation x_i >= 0
    bounds = [(0, None)] * n

    core_allocations = []

    # We need to find the range for each player in the core.
    for i in range(n):
        # Objective: maximize x_i (player i's allocation)
        c_max = [0] * n
        c_max[i] = -1  # We maximize by minimizing the negative

        # Solve the linear program to maximize player i's allocation
        result_max = linprog(c_max, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        # Objective: minimize x_i (player i's allocation)
        c_min = [0] * n
        c_min[i] = 1  # Minimize player i's allocation directly

        # Solve the linear program to minimize player i's allocation
        result_min = linprog(c_min, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if result_max.success and result_min.success:
            max_allocation = result_max.x
            min_allocation = result_min.x
            core_allocations.append((players[i], min_allocation[i], max_allocation[i]))
        else:
            print(f"No feasible core allocation found for player {players[i]}.")

    if core_allocations:
        print("Core exists. Range of allocations in the core:")
        for allocation in core_allocations:
            player, min_val, max_val = allocation
            print(f"{player}: {min_val:.2f} to {max_val:.2f}")
    else:
        print("Core does not exist.")

# Example usage
find_core(characteristic_function)
