def get_distance():
    pass
def move_to(x, y):
    pass
def move_pick_and_return(position):
    pass

def rotate_robot(direction):
    pass

# robot gird search algorithm
def robot_grid_search(start, scan_distance, M, N):
    steps = int(N / scan_distance)
    step_size = scan_distance
    # orient the robot to face up
    position = (0,0)
    for step in range(steps):
        for move_up in range(M):
            distance = get_distance()
            if distance <= scan_distance:
                # pick and return the object home
                move_pick_and_return(position[0], position[1] + distance)
                # return to the last position
                move_to(position[0], position[1])
                move_up -= 1
                step -= 1
                continue
            # rotate the robot to face right
            rotate_robot((1, 0))  # right
            # scan to see if there is an obstacle
            distance = get_distance()
            if distance <= scan_distance:
                # pick and return the object home
                move_pick_and_return(position[0], position[1] + distance)
                # return to the last position
                move_to(position[0], position[1])
                move_up -= 1
                step -= 1
                continue
            # move the robot one step in the up direction
            move_to(position[0], position[1] + 1)
            rotate_robot((0, 1))
        # move the robot the step_size in the up direction
        move_to(position[0], position[1] + step_size)
        position = (position[0], position[1] + step_size)