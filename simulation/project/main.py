import math
from typing import Dict, List, Optional, Any
import random
from itertools import combinations
from .entities import ProductType, Supplier, Station, ProductInstance, Customer, Order

# =====================
# Simulation Constants
# =====================
SIMULATION_DAYS = 30
SUPPLIER_COUNT_MIN = 1
SUPPLIER_COUNT_MAX = 5
CUSTOMER_COUNT_MIN = 5
CUSTOMER_COUNT_MAX = 12
SUPPLIER_LEAD_TIME_MIN = 3.0
SUPPLIER_LEAD_TIME_MAX = 7.0
SUPPLIER_ORDER_COST_MIN = 20.0
SUPPLIER_ORDER_COST_MAX = 60.0
CUSTOMER_LEAD_TIME_MIN = 1.0
CUSTOMER_LEAD_TIME_MAX = 5.0
CUSTOMER_ORDER_COST_MIN = 10.0
CUSTOMER_ORDER_COST_MAX = 30.0
STATION_PROCESS_TIME = {
    1: (2, 5),  # Station 1 min/max
    2: (3, 6),  # Station 2 min/max
    3: (4, 8),  # Station 3 min/max
}
PRODUCT_ID_X = 'x'
PRODUCT_ID_Y = 'y'
PRODUCT_ID_Z = 'z'
PRODUCT_ID_FIRST = 1  # Product type 1
PRODUCT_ID_SECOND = 2  # Product type 2
PRODUCT_VOLUME = {
    PRODUCT_ID_FIRST: 1.0,
    PRODUCT_ID_SECOND: 1.5,
    PRODUCT_ID_X: 2.0,  # Product x has a different volume
    PRODUCT_ID_Y: 1.2,  # Product y has a different volume
    PRODUCT_ID_Z: 1.8,  # Product z has a different volume
}

CUSTOMER_PROBABILITY_TO_ORDER = 0.6  # 60% chance to place an order of some item each day (P(order_one) = P(order_two)  and they are independent)

CUSTOMER_MIN_ORDER_QUANTITY = 3
CUSTOMER_MAX_ORDER_QUANTITY = 10
STATUS_WAITING = "waiting"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
INVENTORY_CAPACITY_LIMIT = 100.0  # Example capacity limit for inventory
HOLDING_COST_PER_UNIT = 1.0  # Example holding cost per unit
# Base inventory constants for each product
PRODUCT_ONE_BASE_INVENTORY_LOW = 1
PRODUCT_ONE_BASE_INVENTORY_HIGH = 10
PRODUCT_TWO_BASE_INVENTORY_LOW = 1
PRODUCT_TWO_BASE_INVENTORY_HIGH = 10
PRODUCT_X_BASE_INVENTORY_LOW = 1
PRODUCT_X_BASE_INVENTORY_HIGH = 10
PRODUCT_Y_BASE_INVENTORY_LOW = 1
PRODUCT_Y_BASE_INVENTORY_HIGH = 10
PRODUCT_Z_BASE_INVENTORY_LOW = 1
PRODUCT_Z_BASE_INVENTORY_HIGH = 10
# MIN_INITIAL_INVENTORY = 5  # Minimum initial inventory for each product type

# =====================
class Inventory:
    """
    Manages inventory, storage capacity, and holding costs.
    """
    def __init__(self, capacity_limit: float, holding_cost_per_unit: float):
        self.items: List[ProductInstance] = []  # List of product instances in inventory
        self.total_volume = 0.0
        self.capacity_limit = capacity_limit
        self.holding_cost_per_unit = holding_cost_per_unit

    def set_random_inventory(self, items: List[ProductInstance]):
        self.items = items
        self.calculate_total_volume()

    def calculate_total_volume(self) -> float:
        total_volume = 0.0
        for item in self.items:
            total_volume += item.product_type.volume_per_unit * item.amount
        self.total_volume = total_volume
        if self.total_volume > self.capacity_limit:
            raise ValueError("Total volume exceeds inventory capacity limit.")
        return self.total_volume

    def add(self, product_instance: ProductInstance):
        if not self.can_store(product_instance):
            raise ValueError("Not enough space in inventory.")
        self.items.append(product_instance)
        self.calculate_total_volume()

    def remove(self, product_type: ProductType, quantity: int):
        pass  # Implement logic to remove product instances

    def can_store(self, product_instance: ProductInstance) -> bool:
        product_volume = product_instance.product_type.volume_per_unit
        if self.total_volume + product_volume > self.capacity_limit:
            return False
        return True

    def calculate_holding_cost(self, current_time: float) -> float:
        pass

    def get_product_instances_by_type(self, product_type: ProductType, include_reserve: bool = False) -> int:
        count = 0
        for item in self.items:
            if item.product_type == product_type and (not include_reserve or item.order_id is None):
                count += item.amount
        return count

class SimulationManager:
    """
    Manages the simulation loop, initializes entities, tracks time and performance.
    """
    def __init__(self):
        pass
        # ...existing code...
        # self.time = 0
        # self.entities = []
        # self.statistics = {}

    def run(self):
        """Run the main simulation loop."""
        pass

    def initialize_entities(self):
        """Initialize all simulation entities (stations, products, etc.)."""
        self.setup_suppliers()
        self.setup_customers()
        self.simulation_days = SIMULATION_DAYS
        self.setup_stations()
        # initialize the products types
        self.setup_products()
        # create the base inventory for the products
        self.setup_inventory()  # Moved inventory setup here

        self.producing_by_demand_only()

    def producing_by_demand_only(self) -> None:
        """
        Produce products only based on the demand calculated from customer orders.
        This method will be called after initializing the customers and their orders.
        """
        for i in range(SIMULATION_DAYS):
            # start by simulation for each day
            # each customer have a CUSTOMER_PROBABILITY_TO_ORDER chance to place an order for each product type
            self.init_customer_order_for_day(self.product_one, self.product_two)
            
            # calculate how much product are needed left to produce to fulfill orders
            stock_one = self.inventory.get_product_instances_by_type(self.product_one)
            stock_two = self.inventory.get_product_instances_by_type(self.product_two)
            demand_one = self.demand_for_product(self.product_one)
            demand_two = self.demand_for_product(self.product_two)
            # calculate how much product are needed to produce
            needed_one = max(0, demand_one - stock_one)
            needed_two = max(0, demand_two - stock_two)
            # find the cheapest supplier for either the first or second product or both
            cheapest_supplier = self.find_cheapest_supplier([self.product_one, self.product_two])
            if cheapest_supplier:
                if needed_one > 0:
                    cheapest_supplier.place_order(self.product_one, needed_one)
                if needed_two > 0:
                    cheapest_supplier.place_order(self.product_two, needed_two)

    def find_cheapest_supplier(self, product_types: List[ProductType]) -> Supplier:
        """
        Find the cheapest supplier for the given product types.
        """
        # Logic to find the cheapest supplier
        # check if We order only from one supplier everything
        cheapest_supplier: Supplier = None
        cost = math.inf
        for supplier in self.suppliers:
            total_cost = 0
            for product_type in product_types:
                cost = supplier.sample_raw_material_cost(product_type)
                total_cost += cost
            if total_cost < cost:
                cheapest_supplier = supplier
                cost = total_cost
        # TODO: check if we order from multiple suppliers
        
        return cheapest_supplier

    def demand_for_product(self, product_type: ProductType) -> int:
        """
        Calculate the total demand for a specific product type based on customer orders.
        """
        total_demand = 0
        for customer in self.customers:
            for order in customer.orders:
                if order.product_type == product_type:
                    total_demand += order.quantity
        return total_demand
    def setup_suppliers(self) -> None:
        """
        Initialize the suppliers for the simulation.
        """
        num_suppliers = random.randint(SUPPLIER_COUNT_MIN, SUPPLIER_COUNT_MAX)
        self.suppliers = [
            Supplier(
                supplier_id=i,
                lead_time=random.uniform(SUPPLIER_LEAD_TIME_MIN, SUPPLIER_LEAD_TIME_MAX),
                fixed_order_cost=random.uniform(SUPPLIER_ORDER_COST_MIN, SUPPLIER_ORDER_COST_MAX),
                raw_material_cost_distribution={}
            ) for i in range(num_suppliers)
        ]

    def setup_customers(self) -> None:
        """
        Initialize the customers for the simulation.
        """
        num_customers = random.randint(CUSTOMER_COUNT_MIN, CUSTOMER_COUNT_MAX)
        self.customers = [
            Customer(
                customer_id=i,
                max_lead_time=random.uniform(CUSTOMER_LEAD_TIME_MIN, CUSTOMER_LEAD_TIME_MAX),
                order_cost=random.uniform(CUSTOMER_ORDER_COST_MIN, CUSTOMER_ORDER_COST_MAX)
            ) for i in range(num_customers)
        ]

    def setup_stations(self) -> None:
        """
        Initialize the stations for the simulation.
        """
        station_one = Station(station_id=1)
        station_two = Station(station_id=2)
        station_three = Station(station_id=3)
        self.stations = [station_one, station_two, station_three]

    def setup_products(self) -> None:
        """
        Initialize all product types for the simulation and assign them as attributes.
        """
        self.product_one = ProductType(
            product_id=PRODUCT_ID_FIRST,
            processing_time_distributions={
                1: 0,  # Station 1
                2: 0,  # Station 2
                3: 0   # Station 3
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_FIRST]
        )
        self.product_two = ProductType(
            product_id=PRODUCT_ID_SECOND,
            processing_time_distributions={
                1: 0,  # Station 1
                2: 0,  # Station 2
                3: 0   # Station 3 (custom for product 2)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_SECOND]
        )
        self.product_x = ProductType(
            product_id=PRODUCT_ID_X,
            processing_time_distributions={
                1: random.uniform(*STATION_PROCESS_TIME[1]),  # Station 1
                2: 0,  # Station 2
                3: 0   # Station 3 (custom for product x)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_X]
        )
        self.product_y = ProductType(
            product_id=PRODUCT_ID_Y,
            processing_time_distributions={
                1: 0,  # Station 1
                2: random.uniform(*STATION_PROCESS_TIME[2]),  # Station 2
                3: 0   # Station 3 (custom for product y)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_Y]
        )
        self.product_z = ProductType(
            product_id=PRODUCT_ID_Z,
            processing_time_distributions={
                1: 0,  # Station 1
                2: 0,  # Station 2
                3: random.uniform(*STATION_PROCESS_TIME[3])   # Station 3 (custom for product z)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_Z]
        )

    def setup_inventory(self) -> None:
        """
        Initialize the base inventory for the products.
        """
        self.inventory = Inventory(
            capacity_limit=INVENTORY_CAPACITY_LIMIT,
            holding_cost_per_unit=HOLDING_COST_PER_UNIT
        )
        self.inventory.set_random_inventory([
            ProductInstance(product_type=self.product_one, order_id=None, amount=random.randint(PRODUCT_ONE_BASE_INVENTORY_LOW, PRODUCT_ONE_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_two, order_id=None, amount=random.randint(PRODUCT_TWO_BASE_INVENTORY_LOW, PRODUCT_TWO_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_x, order_id=None, amount=random.randint(PRODUCT_X_BASE_INVENTORY_LOW, PRODUCT_X_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_y, order_id=None, amount=random.randint(PRODUCT_Y_BASE_INVENTORY_LOW, PRODUCT_Y_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_z, order_id=None, amount=random.randint(PRODUCT_Z_BASE_INVENTORY_LOW, PRODUCT_Z_BASE_INVENTORY_HIGH))
        ])

    def init_customer_order_for_day(self, product_one, product_two) -> None:
        """
        For each customer, randomly decide whether to place an order for each product type for the day.
        """
        for customer in self.customers:
            # to choose whether to order the first item
            v1 = random.random()
            if v1 < CUSTOMER_PROBABILITY_TO_ORDER:
                quantity = random.randint(CUSTOMER_MIN_ORDER_QUANTITY, CUSTOMER_MAX_ORDER_QUANTITY)
                customer.place_order(product_one, quantity)
            # to choose whether to order the second item
            v2 = random.random()
            if v2 < CUSTOMER_PROBABILITY_TO_ORDER:
                quantity = random.randint(CUSTOMER_MIN_ORDER_QUANTITY, CUSTOMER_MAX_ORDER_QUANTITY)
                customer.place_order(product_two, quantity)

    def advance_time_step(self):
        """Advance the simulation by one time step."""
        pass

    def log_statistics(self):
        """Log or print simulation statistics."""
        pass