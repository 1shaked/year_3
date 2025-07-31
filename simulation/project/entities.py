import math
from typing import Dict, List, Any, Optional, Tuple, Union
from consts import *
import numpy as np


# STATION_ID_X = 'PRODUCT_X'
# STATION_ID_Y = 'PRODUCT_Y'
# STATION_ID_Z = f'{STATION_ID_X}_{STATION_ID_Y}_PRODUCT_Z'

class ProductType:
    """
    Represents a type of product with processing time distributions and volume per unit.
    """
    def __init__(self, product_id: int | str, processing_time_distributions: Dict[int, Any], volume_per_unit: float, cost: float = 0.0):
        self.product_id = product_id
        self.processing_time_distributions = processing_time_distributions  # station_id -> distribution
        self.volume_per_unit = volume_per_unit
        self.cost = cost  # Cost per unit of this product type

    def sample_processing_time(self, station_id: int) -> float:
        """Sample processing time for a given station."""
        lambda_value = self.processing_time_distributions.get(station_id)
        if lambda_value:
            val = np.random.exponential(scale=lambda_value, size=1)[0]
            while val > WORKING_DAY_LENGTH or val <= MIN_PROCESSING_TIME:  # Ensure the processing time does not exceed the working day length
                val = round(np.random.exponential(scale=lambda_value, size=1)[0], ROUND_DECIMAL_PLACES)
            return round(val, ROUND_DECIMAL_PLACES)
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
    def __init__(self, product_type: ProductType, order_id: int | None, status: str = INGREDIENTS_WAITING, amount: int = 1 , product_designation: str | None = None):
        '''
        The status can be (INGREDIENTS_WAITING, INGREDIENTS_ORDERED, )
        '''
        self.product_type = product_type
        self.order_id = order_id
        self.status = status
        self.amount = amount
        self.product_designation = product_designation # can be PRODUCT_ID_FIRST , PRODUCT_ID_SECOND , or None

    def __str__(self):
        """String representation of the product instance."""
        return f"ProductInstance(product_id={self.product_type.product_id}, order_id={self.order_id}, status={self.status}, amount={self.amount}, product_designation={self.product_designation})"

    def __repr__(self):
        """Official string representation of the product instance."""
        return (f"ProductInstance(product_id={self.product_type.product_id}, "
                f"order_id={self.order_id}, status={self.status}, amount={self.amount}, product_designation={self.product_designation})")

    def advance_to_next_station(self):
        """Advance this product to the next station in its route."""
        pass

    def get_product_price(self) -> float:
        """Get the price of this product instance."""
        if self.product_type.cost == 0.0:
            raise ValueError("Product type cost is not set.")
        # Assuming the cost is per unit, multiply by the amount
        return self.product_type.cost * self.amount
class Station:
    """
    Represents a processing station with a queue of products.
    """
    def __init__(self, station_id: int):
        self.station_id = station_id
        # the queue holds tuples of (ProductInstance, processing_time)
        self.queue: List[(ProductInstance | List[ProductInstance], float)] = []
        self.working_item_index: Optional[int] = None  # Index of the currently processing item, if any

    def get_next_finish_time(self) -> float:
        """Get the next finish time for the station."""
        if self.queue:
            return self.queue[0][1]
        return math.inf  # If the queue is empty, return infinity

    def get_item_in_queue(self, index: int) -> Tuple[ProductInstance, float ] | None:
        """Get the current queue of product instances."""
        if 0 <= index < len(self.queue):
            return self.queue[index]
        return None
    
    def start_processing(self, index = 0) -> float:
        # check if a list first
        if isinstance(self.queue[index][0], list):
            for item in self.queue[index][0]:
                item.status = STATUS_PROCESSING_MACHINE
        else:
            self.queue[index][0].status = STATUS_PROCESSING_MACHINE
        self.working_item_index = index
        return self.queue[index][1]
    
    def decrement_processing_time(self, index: int, time: float, ) -> Tuple[ProductInstance, float ] | Tuple[None, None]:
        """Decrement the processing time of the product instance at the given index."""
        if 0 <= index < len(self.queue):
            product_instance, processing_time = self.queue[index]
            new_processing_time = max(0, processing_time - time)
            self.queue[index] = (product_instance, new_processing_time)
            if new_processing_time == 0:
                if self.station_id == STATION_THREE_ID:
                    # this mean we are done preparing the product z create the product instance 
                    product_designation = self.queue[index][0][0].product_designation
                    if product_designation is None:
                        raise ValueError("Product designation is None for product z.")
                    
                    # calculate the cost
                    cost = 0.0
                    for item in self.queue[index][0]:
                        cost += item.product_type.cost
                    product_type = ProductType(
                            product_id=product_designation,
                            processing_time_distributions={
                                1: 0,  # Station 1
                                2: 0,  # Station 2
                                3: 0   # Station 3
                            },
                            volume_per_unit=PRODUCT_VOLUME[product_designation],
                            cost=cost
                        )
                    product_instance = ProductInstance(
                        product_type=product_type,
                        order_id=self.queue[index][0][0].order_id,
                        status=STATUS_COMPLETED_MACHINE,
                        amount=self.queue[index][0][0].amount * FACTOR_DICT[product_designation],
                        product_designation=None
                    )
                    self.queue.pop(0)
                    return product_instance, new_processing_time
                product_instance.status = STATUS_COMPLETED_MACHINE
                # pop the first item from the queue
                self.queue.pop(0)
                if len(self.queue) > 0:
                    self.working_item_index = 0
                return product_instance , new_processing_time
            return None , None
        return None , None
    
    

    def decrement_processing_time_for_working_item(self, time: float) -> Tuple[ProductInstance | None, float]:
        """Decrement the processing time of the currently working item."""
        if self.working_item_index is not None:
            return self.decrement_processing_time(self.working_item_index, time)
        return None, 0.0

    def sample_processing_time(self, product_type: ProductType) -> float:
        """Sample processing time for a product type at this station."""
        return product_type.sample_processing_time(self.station_id)

    def add_to_queue(self, product_instance: ProductInstance | List[ProductInstance]) -> float:
        """Add a product instance to the station's queue."""
        if isinstance(product_instance, list):
            # this is only for product z
            processing_time = self.sample_processing_time(product_instance[0].product_type)
            self.queue.append((product_instance, processing_time))
            return processing_time
        processing_time = self.sample_processing_time(product_instance.product_type)
        self.queue.append((product_instance, processing_time))
        return processing_time

    def check_can_be_processed(self) -> bool:
        '''
        This will be needed for the product type z
        '''
        if self.station_id == STATION_ONE_ID:
            # we only need to check if the product is of type x is present in the queue
            if len(self.queue) == 0:
                return None
            return self.queue[0][0].product_type.product_id == PRODUCT_ID_X
        
        if self.station_id == STATION_TWO_ID:
            # we only need to check if the product is of type y is present in the queue
            if len(self.queue) == 0:
                return None
            return self.queue[0][0].product_type.product_id == PRODUCT_ID_Y
        
        # if the product is z then we need to check if the first item have x , y , z
        if self.station_id == STATION_THREE_ID:
            if len(self.queue) == 0:
                return None
            items_needed = [PRODUCT_ID_X, PRODUCT_ID_Y, PRODUCT_ID_Z]
            # check first if list 
            if not isinstance(self.queue[0][0], list):
                raise ValueError("Expected a list of ProductInstances for station three.")
            for item in self.queue[0][0]:
                if item.product_type.product_id in items_needed:
                    # pop the item from the queue
                    items_needed.remove(item.product_type.product_id)
            return len(items_needed) == 0
        
        raise ValueError(f"Unknown station ID: {self.station_id}")
        # return False
    def pop_from_queue(self, index=0) -> Optional[Tuple[ProductInstance, float]]:
        """Pop the next product instance from the queue."""
        if self.queue:
            product_instance, processed_time = self.queue.pop(index)
            return product_instance, processed_time
        return None
    
    def can_be_processed(self, ) -> bool:
        '''This function check if the station have all the resources to process the product in the queue'''
        pass

    def add_processed_item(self, product_instance: ProductInstance):
        # add to the first index
        if len(self.queue) == 0:
            raise ValueError('The queue is empty')
        # we need to find the index of the item which have the same order_id, and the same product_designation
        product_instance.product_designation
        product_instance.order_id
        for index in range(len(self.queue)):
            items_list = self.queue[index][0]
            if not isinstance(items_list , List) or len(items_list) == 0:
                raise ValueError(f'Expected List but did not get it, or the len(item) is empty {len(item)}')
            
            item = None
            for product_item in items_list:
                if product_item.product_type.product_id == PRODUCT_ID_Z:
                    item = product_item
                    break
            if item is None:
                raise ValueError(f'Expend the queue to have item z')
            # item = items_list.
            if item.product_designation == product_instance.product_designation and item.order_id ==product_instance.order_id:
                # add the item to the index
                self.queue[index][0].append(item)
    
class Order:
    """
    Represents an order placed by a customer.
    """
    def __init__(self, order_id: int, products: List[Tuple[ProductType, int]], due_time: float, status: str = INGREDIENTS_WAITING):
        self.order_id = order_id
        self.products = products
        self.due_time = due_time
        self.status = INGREDIENTS_WAITING  # Order status can be 'WAITING', 'INGREDIENTS_ORDERED', INGREDIENTS_PROCESSED ,'ORDER_FULFILLED', etc.

    def __str__(self):
        return f"Order ID: {self.order_id}, Products: {[(product.product_id, quantity) for product, quantity in self.products]}, Due Time: {self.due_time}, Status: {self.status}"
    def __repr__(self):
        return f"Order({self.order_id}, {self.products}, {self.due_time}, {self.status})"
    def mark_fulfilled(self):
        """Mark the order as fulfilled."""
        self.status = ORDER_FULFILLED

    def calculate_order_cost(self) -> float:
        for product, q in self.products:
            if product.cost == 0.0:
                raise ValueError("Product type cost is not set.")
        return sum(product.cost * q for product, q in self.products)
    
    def __str__(self):
        '''String representation of the order for logging purposes'''
        return f"Order ID: {self.order_id}, \nProducts: {[(product.product_id, quantity) for product, quantity in self.products]}, \nDue Time: {self.due_time},\tStatus: {self.status}"

class Customer:
    """
    Represents a customer who places orders.
    """
    def __init__(self, customer_id: int, max_lead_time: float, order_cost: float):
        self.customer_id = customer_id
        self.max_lead_time = max_lead_time
        self.order_cost = order_cost
        self.orders: List[Order] = []

    def place_order(self, products: List[Tuple[ProductType, int]] , day: int) -> None:
        """Place a new order for a product type."""
        order_id = f'{self.customer_id}_{day}_{len(self.orders) + 1}'  # Simple ID generation
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
            if order.status == INGREDIENTS_WAITING or not filter_by_waiting:
                if order.due_time < due_date:
                    due_date = order.due_time
                    closest_order = order
        return closest_order

