from typing import Dict, List, Any, Optional
import random

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
    def __init__(self, product_type: ProductType, order_id: int | None, current_station_index: int = 0, status: str = "waiting", amount: int = 1):
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
