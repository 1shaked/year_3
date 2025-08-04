from consts import *
from main import (
    SimulationManager,

)

# ...existing code...

if __name__ == "__main__":
    for i in range(1, 2):
        for ordering_strategy in ORDERING_STRATEGIES:
            for OPTION in [GET_NEXT_ORDER_OPTIONS[0]]:
                for ALGORITHM in ALGORITHM_SORTING_OPTIONS:
                    sim = SimulationManager(OPTION, ALGORITHM, ordering_strategy)
                    sim.run()