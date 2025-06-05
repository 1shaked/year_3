from typing import Dict, List, Optional, Any
import random

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
class ProductType:
    """
    Represents a type of product with processing time distributions and volume per unit.
    """
    def __init__(self, product_id: int | str, processing_time_distributions: Dict[int, Any], volume_per_unit: float):
        self.product_id = product_id
        self.processing_time_distributions = processing_time_distributions  # station_id -> distribution
        self.volume_per_unit = volume_per_unit

    def sample_processing_time(self, station_id: int) -> float:
        """Sample processing time for a given station."""
        dist = self.processing_time_distributions.get(station_id)
        if dist:
            return dist.sample()
        raise ValueError(f"No distribution for station {station_id}")

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


class Station:
    """
    Represents a processing station with a queue of products.
    """
    def __init__(self, station_id: int):
        self.station_id = station_id
        self.end_processing_time: float | None = None

    def sample_processing_time(self, product_type: ProductType) -> float:
        """Sample processing time for a product type at this station."""
        return product_type.sample_processing_time(self.station_id)

class ProductInstance:
    """
    Represents an instance of a product in the system.
    """
    def __init__(self, product_type: ProductType, order_id: int | None, current_station_index: int = 0, status: str = STATUS_WAITING, amount: int = 1):
        self.product_type = product_type
        self.order_id = order_id
        self.status = status
        self.amount = amount

    def advance_to_next_station(self):
        """Advance this product to the next station in its route."""
        pass

class Customer:
    """
    Represents a customer who places orders.
    """
    def __init__(self, customer_id: int, max_lead_time: float, order_cost: float):
        self.customer_id = customer_id
        self.max_lead_time = max_lead_time
        self.order_cost = order_cost
        self.orders: List[Order] = []

    def place_order(self, product_type: ProductType, quantity: int):
        """Place a new order for a product type."""
        order_id = len(self.orders) + 1  # Simple ID generation
        due_time = self.max_lead_time  # Assuming due time is the max lead time for simplicity
        order = Order(order_id, self, product_type, quantity, due_time)
        self.orders.append(order)

    def is_order_late(self, order: 'Order', current_time: float) -> bool:
        """Check if an order is late."""
        return current_time > order.due_time

class Order:
    """
    Represents an order placed by a customer.
    """
    def __init__(self, order_id: int, customer: Customer, product_type: ProductType, quantity: int, due_time: float, is_fulfilled: bool = False):
        self.order_id = order_id
        self.customer = customer
        self.product_type = product_type
        self.quantity = quantity
        self.due_time = due_time
        self.is_fulfilled = is_fulfilled

    def mark_fulfilled(self):
        """Mark the order as fulfilled."""
        self.is_fulfilled = True

class Supplier:
    """
    Represents a supplier of raw materials.
    """
    def __init__(self, supplier_id: int, lead_time: float, fixed_order_cost: float, raw_material_cost_distribution: Dict[ProductType, Any]):
        self.supplier_id = supplier_id
        self.lead_time = lead_time
        self.fixed_order_cost = fixed_order_cost
        self.raw_material_cost_distribution = raw_material_cost_distribution

    def sample_raw_material_cost(self, product_type: ProductType) -> float:
        """Sample the raw material cost for a product type."""
        dist = self.raw_material_cost_distribution.get(product_type)
        if dist:
            return dist.sample()
        raise ValueError(f"No cost distribution for product type {product_type}")

    def place_order(self, product_type: ProductType, quantity: int):
        """Place an order for raw materials."""
        pass

    def deliver_materials(self, current_time: float):
        """Deliver materials at the given time."""
        pass

class Inventory:
    """
    Manages inventory, storage capacity, and holding costs.
    """
    def __init__(self, capacity_limit: float, holding_cost_per_unit: float):
        # self.stock: Dict[ProductType, int] = { # THIS NEED TO BE CHANGE TO BE RANDOM GENERATED
        #     PRODUCT_ID_FIRST: 0,  # Base inventory for product type 1
        #     PRODUCT_ID_SECOND: 0,  # Base inventory for product type 2
        #     PRODUCT_ID_X: 0,  # Base inventory for product x
        #     PRODUCT_ID_Y: 0,  # Base inventory for product y
        #     PRODUCT_ID_Z: 0   # Base inventory for product z
        # }
        self.items: List[ProductInstance] = []  # List of product instances in inventory
        self.total_volume = 0.0
        self.capacity_limit = capacity_limit
        self.holding_cost_per_unit = holding_cost_per_unit

    def set_random_inventory(self, items: List[ProductInstance]):

        self.items = items

        self.calculate_total_volume()

    def calculate_total_volume(self) -> float:
        """Calculate the total volume of products in stock."""
        total_volume = 0.0
        for item in self.items:
            total_volume += item.product_type.volume_per_unit * item.amount
        self.total_volume = total_volume
        if self.total_volume > self.capacity_limit:
            raise ValueError("Total volume exceeds inventory capacity limit.")
        return self.total_volume

    def add(self, product_instance: ProductInstance):
        """Add a product instance to inventory."""
        if not self.can_store(product_instance):
            raise ValueError("Not enough space in inventory.")
        self.items.append(product_instance)
        self.calculate_total_volume()

    def remove(self, product_type: ProductType, quantity: int):
        """Remove a quantity of a product type from inventory."""
        pass  # Implement logic to remove product instances

    def can_store(self, product_instance: ProductInstance) -> bool:
        """Check if there is enough space to store the product instance."""
        product_volume = product_instance.product_type.volume_per_unit
        if self.total_volume + product_volume > self.capacity_limit:
            return False
        return True

    def calculate_holding_cost(self, current_time: float) -> float:
        """Calculate the holding cost at the current time."""
        pass
    def get_product_instances_by_type(self, product_type: ProductType, include_reserve: bool = False) -> int:
        """Get all product instances of a specific type."""
        count = 0
        for item in self.items:
            if item.product_type == product_type and (not include_reserve or item.order_id is None):
                count += item.amount
        return count
class PricingTable:
    """
    Stores price per unit for each product type.
    """
    def __init__(self, price_per_unit: Dict[ProductType, float]):
        self.price_per_unit = price_per_unit

    def get_price(self, product_type: ProductType) -> float:
        """Get the price per unit for a product type."""
        return self.price_per_unit.get(product_type, 0.0)

class Event:
    """
    Represents an event in an event-based simulation.
    """
    def __init__(self, time: float, event_type: str, associated_entities: Optional[List[Any]] = None):
        self.time = time
        self.event_type = event_type
        self.associated_entities = associated_entities or []

    def execute(self):
        """Execute the event's logic."""
        pass