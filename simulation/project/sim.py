from consts import *
from main import (
    SimulationManager,

)

# ...existing code...

if __name__ == "__main__":
    sim = SimulationManager(GET_NEXT_ORDER_BY_PRICE, )
    sim.run()