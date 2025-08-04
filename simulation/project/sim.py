from consts import *
from main import (
    SimulationManager,

)

# ...existing code...

if __name__ == "__main__":
    for i in range(1, 3):
        for OPTION in GET_NEXT_ORDER_OPTIONS:
            for ALGORITHM in ALGORITHM_SORTING_OPTIONS:
                sim = SimulationManager(OPTION, ALGORITHM)
                sim.run()