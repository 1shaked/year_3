"""Factory simulation with 3 machines, 7 Poisson‑ordering customers and 5 suppliers.
Time unit: minutes. 1 work‑day = 480 minutes (8 hours).
Uses SimPy 4.1.x.  Run with: `python factory_sim.py`.
"""

import random
from typing import Dict
import numpy as np
import simpy

# -------------------------- constants ---------------------------------------
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 8
MINUTES_PER_DAY = HOURS_PER_DAY * MINUTES_PER_HOUR  # 480

# -------------------------- helper functions --------------------------------

def u_minutes(low: int, high: int) -> int:
    """Inclusive uniform integer in [low, high] minutes."""
    return random.randint(low, high)

# -------------------------- core resources ----------------------------------

class Machine:
    """A single‑capacity machine with a stochastic processing time per unit."""

    def __init__(self, env: simpy.Environment, name: str, pt_sampler):
        self.env = env
        self.name = name
        self.res = simpy.Resource(env, capacity=1)
        self.pt_sampler = pt_sampler  # function -> minutes per unit

    def process(self, units: int = 1):
        """Request machine and wait the total processing time."""
        with self.res.request() as req:
            yield req
            duration = sum(self.pt_sampler() for _ in range(units))
            yield self.env.timeout(duration)

# -------------------------- supplier & inventory ----------------------------

class Supplier:
    """Quotes independent prices each time it is asked."""

    def __init__(self, name: str):
        self.name = name

    def quote(self) -> Dict[str, int]:
        return {r: random.randint(7, 15) for r in ("x", "y", "z")}

class Inventory:
    """Very small helper wrapper around a dict of resource levels."""

    def __init__(self):
        self.level: Dict[str, float] = {k: 0 for k in ("x", "y", "z", "x*", "y*")}

    def add(self, res: str, qty: float):
        self.level[res] += qty

    def remove(self, res: str, qty: float):
        if self.level[res] < qty:
            raise RuntimeError(f"Insufficient {res}: need {qty}, have {self.level[res]}")
        self.level[res] -= qty

# -------------------------- factory -----------------------------------------

class Factory:
    def __init__(self, env: simpy.Environment):
        self.env = env
        # machines
        self.m1 = Machine(env, "M1", lambda: u_minutes(10, 20))  # x ➜ x*
        self.m2 = Machine(env, "M2", lambda: u_minutes(10, 20))  # y ➜ y*
        self.m3 = Machine(env, "M3", lambda: u_minutes(15, 25))  # assembly

        # suppliers & inventory
        self.suppliers = [Supplier(f"S{i}") for i in range(1, 6)]
        self.inv = Inventory()

    # ------------------ procurement helpers ------------------

    def procure(self, res: str, qty: float):
        """Order *qty* of *res* from the cheapest supplier (price sampled on request)."""
        quotes = [(s, s.quote()[res]) for s in self.suppliers]
        best, price = min(quotes, key=lambda t: t[1])
        self.inv.add(res, qty)
        print(f"{self.env.now:6.1f} ▶ Bought {qty} {res} from {best.name} at {price}/u (¢={price*qty})")

    # ------------------ production helpers -------------------

    def ensure_x_star(self, qty: float):
        need = qty - self.inv.level["x*"]
        if need <= 0:
            return self.env.timeout(0)
        raw_need = need - self.inv.level["x"]
        if raw_need > 0:
            self.procure("x", raw_need)
        self.inv.remove("x", need)
        print(f"{self.env.now:6.1f} ▶ Start M1 for {need} x→x*")
        yield self.env.process(self.m1.process(int(need)))
        self.inv.add("x*", need)
        print(f"{self.env.now:6.1f} ◀ Finished {need} x*")

    def ensure_y_star(self, qty: float):
        need = qty - self.inv.level["y*"]
        if need <= 0:
            return self.env.timeout(0)
        raw_need = need - self.inv.level["y"]
        if raw_need > 0:
            self.procure("y", raw_need)
        self.inv.remove("y", need)
        print(f"{self.env.now:6.1f} ▶ Start M2 for {need} y→y*")
        yield self.env.process(self.m2.process(int(need)))
        self.inv.add("y*", need)
        print(f"{self.env.now:6.1f} ◀ Finished {need} y*")

    # ------------------ public API ---------------------------

    def build(self, product: str, qty: int = 1):
        """Launch a build order for product A or B (qty units)."""
        if product not in ("A", "B"):
            raise ValueError("product must be 'A' or 'B'")
        return self.env.process(self._build(product, qty))

    def _build(self, product: str, qty: int):
        req_z = qty if product == "A" else qty / 2
        req_xs = qty
        req_ys = qty

        # ensure intermediates/raws
        yield self.env.process(self.ensure_x_star(req_xs))
        yield self.env.process(self.ensure_y_star(req_ys))
        if self.inv.level["z"] < req_z:
            self.procure("z", req_z - self.inv.level["z"])
        # consume
        self.inv.remove("x*", req_xs)
        self.inv.remove("y*", req_ys)
        self.inv.remove("z", req_z)

        print(f"{self.env.now:6.1f} ▶ Start M3 assemble {qty}→{product}")
        yield self.env.process(self.m3.process(qty))
        print(f"{self.env.now:6.1f} ◀ Completed {product} x{qty}")

# -------------------------- customer process -------------------------------

def customer(env: simpy.Environment, name: str, factory: Factory):
    """Each customer places orders following a Poisson process with λ=2 days."""
    while True:
        interarrival = np.random.exponential(scale=2 * MINUTES_PER_DAY)
        yield env.timeout(interarrival)
        product = random.choice(["A", "B"])
        qty = random.randint(1, 3)  # arbitrary batch size
        lead = random.randint(5 * MINUTES_PER_DAY, 12 * MINUTES_PER_DAY)
        print(f"{env.now:6.1f} 🛒 {name} orders {qty}×{product} (due in {lead/ MINUTES_PER_DAY:.1f} d)")
        env.process(factory.build(product, qty))

# -------------------------- main -------------------------------------------

def run_sim(sim_days: int = 30, seed: int | None = 42):
    random.seed(seed)
    np.random.seed(seed)
    env = simpy.Environment()
    factory = Factory(env)
    for i in range(1, 8):
        env.process(customer(env, f"C{i}", factory))
    env.run(until=sim_days * MINUTES_PER_DAY)

if __name__ == "__main__":
    run_sim()
