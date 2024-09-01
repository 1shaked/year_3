from scipy.optimize import linprog
import numpy as np

# Define matrix A and vector B
A = np.array([
    [-1 , 0, 0],
    [0, -1, 0],
    [0, 0, -1],
    [-1, -1, 0],
    [-1, 0, -1],
    [0, -1, -1],
    [-1, -1, -1],
    [1, 1, 1],
])
B = np.array([0, 0, 0, -1, -1, -1, -1, 1])

# Solve linear programs to find the boundary solutions

# Objective function is arbitrary (e.g., minimize x1)
c = [0, 0, 0]  # No specific objective since we are finding feasible points

# Setting bounds for x1, x2, x3
x_bounds = (0, None)
y_bounds = (0, None)
z_bounds = (0, None)

# Linear programming to find feasible region
result = linprog(c, A_ub=A, b_ub=B, bounds=[x_bounds, y_bounds, z_bounds], method='highs')

if result.success:
    print("A feasible solution is:", result.x)
else:
    print("No feasible solution found.")

# For finding all solutions, we would explore the space around these solutions using additional constraints or by looking for vertices
