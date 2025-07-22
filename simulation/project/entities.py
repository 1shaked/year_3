import math
from typing import Dict, List, Any, Optional, Tuple
from typing import Union

from main import PRODUCT_ID_Z, STATUS_COMPLETED, STATUS_PROCESSING, STATUS_WAITING

WAITING = 'WAITING'
INGREDIENTS_ORDERED = 'INGREDIENTS_ORDERED'
FULFILLED = 'FULFILLED'

# STATION_ID_X = 'PRODUCT_X'
# STATION_ID_Y = 'PRODUCT_Y'
# STATION_ID_Z = f'{STATION_ID_X}_{STATION_ID_Y}_PRODUCT_Z'

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
        self.orders : List[Dict[float, Dict[str, Any]]] = []

    def sample_raw_material_cost(self, product_type: ProductType) -> float:
        """Sample the raw material cost for a product type."""
        dist = self.raw_material_cost_distribution.get(product_type)
        if dist:
            return dist
        raise ValueError(f"No cost distribution for product type {product_type}")

    def place_order(self, product_types: List[tuple[ProductType, int]], current_time: float) -> float:
        """Place an order for raw materials."""
        order_cost = self.fixed_order_cost

        for product_type, quantity in product_types:
            material_cost = self.sample_raw_material_cost(product_type)
            order_cost += material_cost * quantity
        self.orders.append({
            'products': product_types,
            'order_cost': order_cost,
            'due_time': current_time + self.lead_time
        })
        return order_cost

    def deliver_materials(self, current_time: float):
        """Deliver materials at the given time."""
        pass


class ProductInstance:
    """
    Represents an instance of a product in the system.
    """
    def __init__(self, product_type: ProductType, order_id: int | None, status: str = STATUS_WAITING, amount: int = 1):
        '''
        The status can be (STATUS_WAITING STATUS_PROCESSING, STATUS_COMPLETED)
        '''
        self.product_type = product_type
        self.order_id = order_id
        self.status = status
        self.amount = amount

    def advance_to_next_station(self):
        """Advance this product to the next station in its route."""
        pass
class Station:
    """
    Represents a processing station with a queue of products.
    """
    def __init__(self, station_id: int):
        self.station_id = station_id
        # the queue holds tuples of (ProductInstance, processing_time)
        self.queue: List[(ProductInstance, float)] = []
        self.working_item_index: Optional[int] = None  # Index of the currently processing item, if any


    def get_item_in_queue(self, index: int) -> Tuple[ProductInstance, float ] | None:
        """Get the current queue of product instances."""
        if 0 <= index < len(self.queue):
            return self.queue[index]
        return None
    
    def start_processing(self, index) -> float:
        self.queue[index][0].status = STATUS_PROCESSING
        self.working_item_index = index
        return self.queue[index][1]
    
    def decrement_processing_time(self, index: int, time: float) -> Tuple[ProductInstance | None, float]:
        """Decrement the processing time of the product instance at the given index."""
        if 0 <= index < len(self.queue):
            product_instance, processing_time = self.queue[index]
            new_processing_time = max(0, processing_time - time)
            self.queue[index] = (product_instance, new_processing_time)
            if new_processing_time == 0:
                product_instance.status = STATUS_COMPLETED
                self.working_item_index = None
            return product_instance , new_processing_time
        return None , 0.0
    
    def decrement_processing_time_for_working_item(self, time: float) -> Tuple[ProductInstance | None, float]:
        """Decrement the processing time of the currently working item."""
        if self.working_item_index is not None:
            return self.decrement_processing_time(self.working_item_index, time)
        return None, 0.0

    def sample_processing_time(self, product_type: ProductType) -> float:
        """Sample processing time for a product type at this station."""
        return product_type.sample_processing_time(self.station_id)

    def add_to_queue(self, product_instance: ProductInstance) -> float:
        """Add a product instance to the station's queue."""
        processing_time = self.sample_processing_time(product_instance.product_type)
        self.queue.append((product_instance, processing_time))
        # self.queue.sort(key=lambda x: x[1])
        return processing_time

    def check_can_be_processed(self, product: ProductType) -> bool:
        '''
        This will be needed for the product type z
        '''
        if product.product_id == PRODUCT_ID_Z:
            # we need to check that product x and y are processed before product z

            pass
        # Check if the product can be processed at this station
        pass

    def pop_from_queue(self, index=0) -> Optional[Tuple[ProductInstance, float]]:
        """Pop the next product instance from the queue."""
        if self.queue:
            product_instance, processed_time = self.queue.pop(index)
            return product_instance, processed_time
        return None
    
    def can_be_processed(self, ) -> bool:
        '''This function check if the station have all the resources to process the product in the queue'''
        pass
    
class Order:
    """
    Represents an order placed by a customer.
    """
    def __init__(self, order_id: int, products: List[Tuple[ProductType, int]], due_time: float, status: str = 'WAITING'):
        self.order_id = order_id
        self.products = products
        self.due_time = due_time
        self.status = WAITING  # Order status can be 'WAITING', 'INGREDIENTS_ORDERED', 'FULFILLED', etc.

    def mark_fulfilled(self):
        """Mark the order as fulfilled."""
        self.status = FULFILLED

class Customer:
    """
    Represents a customer who places orders.
    """
    def __init__(self, customer_id: int, max_lead_time: float, order_cost: float):
        self.customer_id = customer_id
        self.max_lead_time = max_lead_time
        self.order_cost = order_cost
        self.orders: List[Order] = []

    def place_order(self, products: List[Tuple[ProductType, int]]):
        """Place a new order for a product type."""
        order_id = len(self.orders) + 1  # Simple ID generation
        due_time = self.max_lead_time  # Assuming due time is the max lead time for simplicity
        order = Order(order_id, products, due_time)
        self.orders.append(order)

    def is_order_late(self, order: Order, current_time: float) -> bool:
        """Check if an order is late."""
        return current_time > order.due_time
    
    def get_closest_order(self, filter_by_waiting: bool = True) -> Order | None: 
        """Get the closest order that is not yet fulfilled."""
        due_date = math.inf
        closest_order = None
        for order in self.orders:
            if order.status == WAITING or not filter_by_waiting:
                if order.due_time < due_date:
                    due_date = order.due_time
                    closest_order = order
        return closest_order

