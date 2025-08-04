import math
import random
from typing import Dict, List, Optional, Any, Tuple
from itertools import combinations
from consts import *
from entities import INGREDIENTS_WAITING, Order, ProductType, Supplier, Station, ProductInstance, Customer
import json
from datetime import datetime
# =====================
# Simulation Constants (1)
# =====================



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
        

    def __str__(self):
        '''String that will contain the inventory items'''
        s = ''
        for item in self.items:
            s += f'{item.product_type.product_id} (Order ID: {item.order_id}, Amount: {item.amount})\n'
        return s

    def set_random_inventory(self, items: List[ProductInstance]):
        self.items = items
        self.calculate_total_volume()

    def get_products_for_order(self, order_id: int) -> List[ProductInstance]:
        products = []
        for item in self.items:
            if item.order_id == order_id:
                products.append(item)
        return products

    def calculate_total_volume(self) -> float:
        # TODO: if there is an overflow normalize the volume
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
        # before adding check if the product_instance already exists in the inventory with the same order_id and status
        for item in self.items:
            if item.product_type == product_instance.product_type and item.order_id == product_instance.order_id and item.status == product_instance.status and item.product_designation == product_instance.product_designation:
                item.amount += product_instance.amount
                self.calculate_total_volume()
                return
        product_instance.amount = round(product_instance.amount, ROUND_DECIMAL_PLACES)    
        self.items.append(product_instance)
        self.calculate_total_volume()

    def remove(self, product_type: ProductType, quantity: int):
        pass  # Implement logic to remove product instances

    def can_store(self, product_instance: ProductInstance) -> bool:
        product_volume = product_instance.product_type.volume_per_unit
        if self.total_volume + product_volume > self.capacity_limit:
            return False
        return True

    def calculate_holding_cost(self,) -> float:
        holding_cost = 0.0
        for item in self.items:
            holding_cost += item.amount * self.holding_cost_per_unit
        return holding_cost

    def check_capacity_for_product(self, product: ProductType, quantity: int) -> bool:
        """Check if there is enough of a product in the stock"""
        return self.get_product_instances_by_type(product) >= quantity
    

    def has_sufficient_ingredients(self, ingredients: Dict[ProductType, int], order_id: str| None , status: str | None) -> bool:
        """
        Check if the inventory has sufficient ingredients for the given product types and quantities.
        """
        for product_type, quantity in ingredients.items():
            if self.get_product_instances_by_type(product_type, order_id=order_id, status=status) < quantity:
                return False
        return True

    def get_product_instances_by_type(self, product_type: ProductType, order_id: str | None = None, status: str | None = INGREDIENTS_WAITING) -> int:
        '''
        Get the total number of product instances of a specific type.
        If include_reserve is True, it includes instances with order_id None (reserve stock).
        
        '''
        count = 0
        for item in self.items:
            if item.product_type.product_id == product_type.product_id and (order_id is None or item.order_id == order_id) and (status is None or item.status == status):
                count += item.amount
        return count
    
    def have_amount_in_stock_by_order(self, product_type: ProductType, order_id: int, amount: int) -> bool:
        """
        Check if the inventory has a specific amount of a product type for a given order.
        """
        return self.get_product_instances_by_type_and_order(product_type, order_id, None) >= amount
    
    def have_amount_in_stock_product_in_order(self, product_type: Dict[ProductType, int], order_id: int) -> bool:
        """
        Check if the inventory has a specific amount of a products type for a given order.
        """
        for pt, qty in product_type.items():
            if not self.have_amount_in_stock_by_order(pt, order_id, qty):
                return False
        return True

    def get_product_instances_by_type_and_order(self, product_type: ProductType, order_id: int, status: str | None) -> int:
        """
        Get the total number of product instances of a specific type for a given order.
        """
        count = 0
        for item in self.items:
            if item.product_type == product_type and item.order_id == order_id and (status is None or item.status == status):
                count += item.amount
        return count

    def pull_resource_from_stock(self, product_type: ProductType, quantity: int, order_id: str | None = None , status : str | None=INGREDIENTS_WAITING) -> Optional[ProductInstance]:
        """
        Pull a resource from the stock if available.
        Returns the pulled product instance or None if not enough stock.
        """
        for index in range(len(self.items)):
            item = self.items[index]
            if item.product_type.product_id == product_type.product_id and (order_id is None or item.order_id == order_id) and (status is None or item.status == status):
                if item.amount >= quantity:
                    item.amount -= quantity
                    if item.amount == 0:
                        self.items.pop(index)
                    self.calculate_total_volume()
                    # create a copy of the item to return
                    pulled_item = ProductInstance(product_type=item.product_type, order_id=item.order_id, status=item.status, amount=quantity)
                    return pulled_item
                elif item.amount < quantity: 
                    raise ValueError(f"Not enough stock for {product_type.product_id}. Requested: {quantity}, Available: {item.amount}")
        return None

    def pull_resources_from_stock_by_order(self, order: Order, order_id: str | None = None, status: str = INGREDIENTS_WAITING) -> List[ProductInstance]:
        """
        Pull resources from stock based on the order.
        Returns a list of pulled product instances.
        """
        pulled_items = []
        for product_type, quantity in order.products:
            item = self.pull_resource_from_stock(product_type, quantity, order_id=order_id, status=status)
            if item:
                item.order_id = order.order_id  # Set the order ID for the pulled item
                pulled_items.append(item)
            else:
                raise ValueError(f"Not enough stock to fulfill order for {product_type.product_id}.")
        return pulled_items
    
    def pull_resources_from_available_place(self, order: Order) -> List[ProductInstance]:
        pulled_items = []
        for product_type, quantity in order.products:
            # we need to check if we first find item prepared for the order else we look for the item in stock
            quantity_available_produced = self.get_product_instances_by_type(product_type, order_id=order.order_id, status=None)
            if quantity_available_produced >= quantity:
                # we pull the resource from the stock
                pulled_item = self.pull_resource_from_stock(product_type, quantity, order_id=order.order_id, status=None)
                if not pulled_item:
                    raise ValueError(f"Not enough prepared items for {product_type.product_id}. Requested: {quantity}, Available: {quantity_available_produced}")
                
                # delete for the inventory all the product with the same product_designation and order_id
                for item in self.items:
                    if item.product_designation == product_type.product_id and item.order_id == order.order_id:
                        self.items.remove(item)
                pulled_items.append(pulled_item)
                continue

            # we need to check if the item is in stock
            quantity_available_in_stock = self.get_product_instances_by_type(product_type, order_id=None, status=None)
            if quantity_available_in_stock >= quantity:
                # we pull the resource from the stock
                pulled_item = self.pull_resource_from_stock(product_type, quantity, order_id=None, status=None)
                if pulled_item:
                    pulled_items.append(pulled_item)
        return pulled_items
    def pull_resources_from_components_dict(self, components_dict: Dict[ProductType, int], order_id: str | None = None, status: str = INGREDIENTS_WAITING) -> List[ProductInstance]:
        """
        Pull resources from stock based on a components dictionary.
        Returns a list of pulled product instances.
        """
        pulled_items = []
        for product_type, quantity in components_dict.items():
            item = self.pull_resource_from_stock(product_type, quantity, order_id=order_id, status=status)
            if item:
                item.order_id = None  # Set the order ID for the pulled item
                pulled_items.append(item)
            else:
                raise ValueError(f"Not enough stock to fulfill request for {product_type.product_id}.")
        return pulled_items

    def check_if_has_in_stock(self, product_type: ProductType, quantity: int, order_id: str | None = None, status: str | None = INGREDIENTS_WAITING) -> bool:
        """
        Check if the inventory has sufficient stock of a specific product type.
        """
        return self.get_product_instances_by_type(product_type, order_id=order_id, status=status) >= quantity

    def check_if_order_in_stock(self, order: Order) -> bool:
        """
        Check if the inventory has sufficient stock to fulfill an order.
        """
        for product_type, quantity in order.products:
            is_prepared = self.check_if_has_in_stock(product_type, quantity, order_id=order.order_id, status=None)
            is_in_stock = self.check_if_has_in_stock(product_type, quantity)
            if not (is_prepared or is_in_stock):
                return False
        return True

    def check_if_order_is_produced(self, order: Order) -> bool:
        '''
        This function checks if all products in the order are produced and ready for delivery.
        '''
        for product_type, quantity in order.products:
            is_prepared = self.check_if_has_in_stock(product_type, quantity, order_id=order.order_id, status=None)
            if not is_prepared :
                return False
        return True
    
    def remove_products_by_designation(self, product_designation: str, order_id: str) -> None:
        """
        Remove all products with a specific designation and order ID from the inventory.
        """
        self.items = list(filter(lambda item: not (item.product_designation == product_designation and item.order_id == order_id), self.items))

    def has_product_in_status(self, product_type: ProductType , order_id: str | None, quantity: int, status: str=INGREDIENTS_READY_TO_PROCESS) -> bool:
        """
        Check if the inventory has a specific product type in a given status.
        """
        product_type = self.get_product_instances_by_type(product_type, order_id=order_id, status=status)
        return product_type >= quantity

    def to_dict(self) -> Dict[str, Any]:
        """ Convert the inventory to a dictionary representation. """
        return dict(
            items=[item.to_dict() for item in self.items],
            capacity_limit=self.capacity_limit,
            total_volume=self.total_volume,
            holding_cost_per_unit=self.holding_cost_per_unit
        )
    
    def get_total_volume(self) -> float:
        """ Get the total volume of the inventory. """
        return self.total_volume
    
    def get_holding_cost(self) -> float:
        return self.total_volume * HOLDING_COST_PER_UNIT
    
class SimulationManager:
    """
    Manages the simulation loop, initializes entities, tracks time and performance.
    """
    def __init__(self, get_next_order_by: str = GET_NEXT_ORDER_BY_DUE_DATE, algorithm: str = ALGORITHM_EDD, ordering_strategy: str = DEMAND_ONLY):
        self.time : int = 0
        self.orders_fulfilled = set()
        self.orders_fulfilled_list = []
        self.total_income = 0.0
        self.json_info = dict()
        self.get_next_order_by = get_next_order_by
        self.algorithm = algorithm  # Default algorithm
        self.orders_filled_today = []
        self.processing_time_per_order: Dict[str, Dict[str, float]] = dict() # for each order_id we will store the processing time per station
        self.avg_demand_per_day_product_one = []
        self.avg_demand_per_day_product_two = []
        self.ordering_strategy = ordering_strategy

    def register_demand(self, product: ProductType, quantity: int) -> None:
        """Register the demand for a product."""
        if product == self.product_one:
            if len(self.avg_demand_per_day_product_one) >= MAX_PREVIOUS_ORDERS:
                self.avg_demand_per_day_product_one.pop(0)
            self.avg_demand_per_day_product_one.append(quantity)
        elif product == self.product_two:
            if len(self.avg_demand_per_day_product_two) >= MAX_PREVIOUS_ORDERS:
                self.avg_demand_per_day_product_two.pop(0)
            self.avg_demand_per_day_product_two.append(quantity)
        else:
            raise ValueError(f"Unknown product type: {product.product_id}")
        
    def get_demand_for_product(self, product: ProductType ) -> float:
        count = 0
        for customer in self.customers:
            count += customer.get_demand_for_product(product, self.time)
        return count

    def run(self):
        self.initialize_entities()
        self.producing_by_demand_only()

    def initialize_entities(self, algorithm=ALGORITHM_EDD):
        """Initialize all simulation entities (stations, products, etc.)."""
        # initialize the products types
        self.setup_products()
        self.v = {
            self.product_one: {(self.product_x, 1), (self.product_y, 1), (self.product_z, 1)},
            self.product_two: {(self.product_x, 1), (self.product_y, 1), (self.product_z, 1)},
        }
        self.setup_suppliers()
        self.setup_customers()
        self.setup_stations()
        # create the base inventory for the products
        self.setup_inventory()  # Moved inventory setup here
        self.save_current_state()
        
    def save_current_state(self, ) -> None:
        self.json_info[INITIAL_PRODUCTS_KEY] = [self.product_one.to_dict(), self.product_two.to_dict(), 
                                                self.product_x.to_dict(), self.product_y.to_dict(), self.product_z.to_dict()
                                                ]
        self.json_info[SUPPLIER_KEY] = [supplier.to_dict() for supplier in self.suppliers]
        self.simulation_days = SIMULATION_DAYS
        self.json_info[SIMULATION_DAYS_KEY] = SIMULATION_DAYS
        self.json_info[STATIONS_KEY] = [station.to_dict() for station in self.stations]
        self.json_info[INVENTORY_KEY] = [item.to_dict() for item in self.inventory.items]
        temp_v_json = {}
        for product, ingredients in self.v.items():
            temp_v_json[product.product_id] = [{"id": ing[0].product_id, "quantity": ing[1]} for ing in ingredients]
        self.json_info[RECIPE_KEY] = temp_v_json
        self.json_info[ALGORITHM_KEY] = self.algorithm
        self.json_info[TYPE_GET_NEXT_ORDER_BY_KEY] = self.get_next_order_by
        self.json_info[TYPE_PROCESSING_TIME_DISTRIBUTIONS] = STATION_PROCESSING_TIME_LAMBDA
        self.json_info[TYPE_PROBABILITY_TO_ORDER] = CUSTOMER_PROBABILITY_TO_ORDER
        self.json_info[TYPE_STRATEGY_ORDER] = self.ordering_strategy
    def get_closest_order_lead_time(self, filter_by_waiting: bool = False) -> float | None:
        order = self.get_closest_order(filter_by_waiting)
        return order.due_time if order else None


    def sort_stations_by_processing_time(self) -> List[Station]:
        """
        Sort stations by their processing time.
        Returns a list of stations sorted by processing time.
        """
        for station in self.stations:
            # when sorting we also need to check if the station can process the items in the queue
            can_process = []
            can_not_process = []
            for index, item in enumerate(station.queue):
                if station.check_can_be_processed(index):
                    can_process.append(item)
                else:
                    can_not_process.append(item)
            # sort by processing time
            can_process.sort(key=lambda x: x[1])
            can_not_process.sort(key=lambda x: x[1])
            # join the two lists
            station.queue = can_process + can_not_process
    def sort_stations_by_lpt(self):
        '''
        Sort the stations by their processing time in descending order.
        '''
        for station in self.stations:
            # when sorting we also need to check if the station can process the items in the queue
            can_process = []
            can_not_process = []
            for index, item in enumerate(station.queue):
                if station.check_can_be_processed(index):
                    can_process.append(item)
                else:
                    can_not_process.append(item)
            # sort by processing time
            can_process.sort(key=lambda x: x[1], reverse=True)
            can_not_process.sort(key=lambda x: x[1], reverse=True)
            # join the two lists
            station.queue = can_process + can_not_process

    def sort_stations_by_edd(self):
        '''
        We will sort the stations by the due time of the order the items are related to.
        '''
        for station in self.stations:
            items_to_sort = []
            # when sorting we also need to check if the station can process the items in the queue
            for index, item in enumerate(station.queue):
                if station.check_can_be_processed(index):
                    if isinstance(item[0], list):
                        order = self.find_order_by_id(item[0][0].order_id)
                        items_to_sort.append((item, order.due_time))
                    else:
                        order = self.find_order_by_id(item[0].order_id)
                        items_to_sort.append((item, order.due_time))
                else:
                    items_to_sort.append((item, math.inf))  # If not processable, set due time to infinity
            # we will sort the orders by their due time
            items_to_sort.sort(key=lambda x: x[1])
            # now we will sort the station queue by the due time of the order
            station.queue = [item for item, _ in items_to_sort]

    def sort_stations_by_critical_ratio(self):
        """ Sort the stations by the critical ratio of the orders in the queue.
        The critical ratio is calculated as (due time - current time) / processing time.
        """
        for station in self.stations:
            items_to_sort = []
            # when sorting we also need to check if the station can process the items in the queue
            for index, item in enumerate(station.queue):
                if station.check_can_be_processed(index):
                    if isinstance(item[0], list):
                        order = self.find_order_by_id(item[0][0].order_id)
                        cr_score = (order.due_time - self.time) / item[1] if item[1] > 0 else math.inf
                        items_to_sort.append((item, cr_score))
                    else:
                        order = self.find_order_by_id(item[0].order_id)
                        cr_score = (order.due_time - self.time) / item[1] if item[1] > 0 else math.inf
                        items_to_sort.append((item, cr_score))
                else:
                    items_to_sort.append((item, math.inf))  # If not processable, set due time to infinity
            # we will sort the orders by their due time
            items_to_sort.sort(key=lambda x: x[1])
            # now we will sort the station queue by the due time of the order
            station.queue = [item for item, _ in items_to_sort]


    def sort_stations_by_slack(self):
        """ Sort the stations by the slack time of the orders in the queue.
        The slack time is calculated as (due time - current time - processing time).
        """
        for station in self.stations:
            items_to_sort = []
            # when sorting we also need to check if the station can process the items in the queue
            for index, item in enumerate(station.queue):
                processing_time = item[1]
                if station.check_can_be_processed(index):
                    if isinstance(item[0], list):
                        order = self.find_order_by_id(item[0][0].order_id)
                        slack_time = order.due_time - self.time - processing_time
                        items_to_sort.append((item, slack_time))
                    else:
                        order = self.find_order_by_id(item[0].order_id)
                        slack_time = order.due_time - self.time - processing_time
                        items_to_sort.append((item, slack_time))
                else:
                    items_to_sort.append((item, math.inf))  # If not processable, set due time to infinity
            # we will sort the orders by their due time
            items_to_sort.sort(key=lambda x: x[1])
            # now we will sort the station queue by the due time of the order
            station.queue = [item for item, _ in items_to_sort]


    def sort_stations_by_algorithm(self, ):
        """ Sort the stations based on the specified algorithm.
        """
        if self.algorithm == ALGORITHM_EDD:
            self.sort_stations_by_edd()
        elif self.algorithm == ALGORITHM_SLACK:
            self.sort_stations_by_slack()
        elif self.algorithm == ALGORITHM_CRITICAL_RATIONAL:
            self.sort_stations_by_critical_ratio()
        elif self.algorithm == ALGORITHM_LPT:
            self.sort_stations_by_lpt()
        elif self.algorithm == ALGORITHM_SPT:
            self.sort_stations_by_processing_time()
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

    def find_order_by_id(self, order_id: str) -> Optional[Order]:
        """
        Find an order by its ID.
        """
        for customer in self.customers:
            for order in customer.orders:
                if order.order_id == order_id:
                    return order
        return None

    def get_closest_order(self, filter_by_waiting: bool = True) -> Order | None:
        """
        Get the closest order that is not yet fulfilled.
        If filter_by_waiting is True, only consider orders that are waiting.
        """
        if self.get_next_order_by == GET_NEXT_ORDER_BY_DUE_DATE:
            return self.get_closest_order_by_due_time(filter_by_waiting)
        elif self.get_next_order_by == GET_NEXT_ORDER_BY_PRICE:
            return self.get_closest_order_by_order_price(filter_by_waiting)
        else:
            raise ValueError(f"Unknown GET_BY parameter: {self.get_next_order_by}")

    def get_closest_order_by_due_time(self, filter_by_waiting: bool = True) -> Order | None:
        """
        Get the closest order by due time that is not yet fulfilled.
        If filter_by_waiting is True, only consider orders that are waiting.
        """
        due_date = math.inf
        closest_order = None
        for customer in self.customers:
            orders = customer.orders
            if not orders:
                continue
            for order in orders:
                can_add = self.can_order_added_to_queue(order)
                if not can_add:
                    print(f"Cannot add order {order.order_id} to queue due to insufficient station capacity.")
                    continue
                # if the order is not fulfilled and is waiting or we don't filter by waiting
                if order and (order.status == INGREDIENTS_WAITING or not filter_by_waiting):
                    if order.due_time < due_date:
                        due_date = order.due_time
                        closest_order = order
        return closest_order
    
    def can_order_added_to_queue(self, order: Order) -> float:
        """
        Calculate the total volume of the order.
        """
        tree = self.get_tree_from_products_list(order.products)
        can_process = True
        for product_type, quantity in tree.items():
            station = self.get_station_by_station_id(PRODUCT_ID_TO_STATION_ID[product_type.product_id])
            total_volume = product_type.volume_per_unit * quantity
            if station is None:
                raise ValueError(f"Station for product {product_type.product_id} not found.")
            if not station.can_add_volume(total_volume):
                can_process = False
                print(f"Cannot add order {order.order_id} to station {station.station_id} due to insufficient volume capacity.")
                break
        return can_process

    def get_closest_order_by_order_price(self, filter_by_waiting: bool = True) -> Order | None:
        """
        Get the closest order by order size that is not yet fulfilled.
        If filter_by_waiting is True, only consider orders that are waiting.
        """
        order_price = 0
        closest_order = None
        for customer in self.customers:
            orders = customer.orders
            if not orders:
                continue
            for order in orders:
                can_add = self.can_order_added_to_queue(order)
                if not can_add:
                    print(f"Cannot add order {order.order_id} to queue due to insufficient station capacity.")
                    continue
                # if the order is not fulfilled and is waiting or we don't filter by waiting
                if order and (order.status == INGREDIENTS_WAITING or not filter_by_waiting):
                    if order.calculate_order_cost() > order_price:
                        order_price = order.calculate_order_cost()
                        closest_order = order
        if closest_order is None:
            print("No orders found that can be processed.")
            return None
        return closest_order

    def receive_supplier_orders(self,):
        # update the inventory based on the suppliers orders received, (by the due date)
        for supplier in self.suppliers:
            for order in supplier.orders:
                if order['due_time'] == self.time:
                    # add the products to the inventory
                    for product_type, quantity in order['products']:
                        product_instance = ProductInstance(product_type=product_type, order_id=None, amount=quantity)
                        self.inventory.add(product_instance)

    def order_missing_components_to_produce(self,):
        # calculate how much product are needed left to produce to fulfill orders
        stock_one = self.inventory.get_product_instances_by_type(self.product_one)
        stock_two = self.inventory.get_product_instances_by_type(self.product_two)
        demand_one = self.demand_for_product(self.product_one)
        demand_two = self.demand_for_product(self.product_two)
        # calculate how much product are needed to produce
        needed_one = max(0, demand_one - stock_one)
        needed_two = max(0, demand_two - stock_two)
        ingredients = self.get_tree_from_products_list([(self.product_one , needed_one * EXTRA_INGREDIENTS_ORDERED_FACTOR) , (self.product_two, needed_two * EXTRA_INGREDIENTS_ORDERED_FACTOR)])
        # find the cheapest supplier for either the first or second product or both
        # transform the ingredients into a list of product types and their quantities
        
        needed_ingredients = list(ingredients.items())
        closest_lead_time = self.get_closest_order_lead_time()
        cheapest_supplier = None
        count = 0
        while cheapest_supplier is None:
            closest_lead_time_with_none = closest_lead_time if closest_lead_time is not None else 0
            cheapest_supplier = self.find_cheapest_supplier(needed_ingredients, closest_lead_time_with_none + count )
            count += 1
        cheapest_supplier.place_order(needed_ingredients, self.time)
        return needed_ingredients , closest_lead_time , cheapest_supplier 

    def eoq(self,) -> float:
        order_cost = math.mean(supplier.order_cost for supplier in self.suppliers)
        holding_cost = self.inventory.holding_cost_per_unit
        demand = math.mean(math.mean(self.avg_demand_per_day_product_one) + math.mean(self.avg_demand_per_day_product_two)) if self.avg_demand_per_day_product_one and self.avg_demand_per_day_product_two else 20
        return math.sqrt((2 * order_cost * demand) / holding_cost)

    def order_missing_components_to_produce_by_eoq(self,):
        # calculate how much product are needed left to produce to fulfill orders
        stock_one = self.inventory.get_product_instances_by_type(self.product_one)
        demand_one = self.demand_for_product(self.product_one)
        # calculate how much product are needed to produce
        needed_one = self.eoq() if self.avg_demand_per_day_product_one else  max(0, demand_one - stock_one)
        ingredients = self.get_tree_from_products_list([(self.product_one , needed_one) ])
        # find the cheapest supplier for either the first or second product or both
        # transform the ingredients into a list of product types and their quantities
        
        needed_ingredients = list(ingredients.items())
        closest_lead_time = self.get_closest_order_lead_time()
        cheapest_supplier = None
        count = 0
        while cheapest_supplier is None:
            closest_lead_time_with_none = closest_lead_time if closest_lead_time is not None else 0
            cheapest_supplier = self.find_cheapest_supplier(needed_ingredients, closest_lead_time_with_none + count )
            count += 1
        cheapest_supplier.place_order(needed_ingredients, self.time)
        return needed_ingredients , closest_lead_time , cheapest_supplier 
    def send_order_in_stock(self,closest_order: Order, ) -> Tuple[Order, float]:
        '''
        We find if there is any combination which either products are in the stock by either production or inventory.
        '''
        pulled_items = self.inventory.pull_resources_from_available_place(closest_order)
        closest_order.mark_fulfilled()
        print('-' * 50)
        print(f"Order {closest_order.order_id} is fulfilled with items: {pulled_items}.")
        print('-' * 50)
        if closest_order.order_id in self.orders_fulfilled:
            raise ValueError(f"Order {closest_order.order_id} is already fulfilled.")
        self.orders_fulfilled_list.append(closest_order)
        self.orders_filled_today.append(closest_order)
        # delete the order from the customer's orders
        for customer in self.customers:
            if closest_order in customer.orders:
                customer.orders.remove(closest_order)
        self.orders_fulfilled.add(closest_order.order_id)
        income = closest_order.calculate_order_cost()
        self.total_income += income
        closest_order = self.get_closest_order(True)
        closest_lead_time = closest_order.due_time if closest_order else None
        return closest_order, closest_lead_time
    
    def handle_no_components_in_stock(self, closest_order: Order) -> Tuple[Order, float]:
        """
        Handle the case when there are no components in stock to fulfill the closest order.
        This will update the order status and find the next closest order.
        """
        print(f"Not enough components in stock to fulfill order {closest_order.order_id}.")
        closest_order.status = INGREDIENTS_ORDERED
        # get next closest order
        closest_order = self.get_closest_order(True)
        closest_lead_time = closest_order.due_time if closest_order else None
        if closest_order is None:
            print("No more orders to process.")
            return None, None
        return closest_order, closest_lead_time
        

    def get_station_by_station_id(self, station_id: str | int) -> Optional[Station]:
        """
        Get a station by its ID.
        """
        for station in self.stations:
            if station.station_id == station_id:
                return station
        return None
    def add_items_from_order_to_station(self, closest_order: Order) -> None:
        """
        Add items from the closest order to the respective station queues.
        This will be called after pulling resources from the inventory.
        """
        closest_order.status = INGREDIENTS_READY_TO_PROCESS
        for product , q in closest_order.products:
            product_resources = self.get_tree_from_products_list([(product, q)])
            pulled_items = self.inventory.pull_resources_from_components_dict(product_resources)
            for item in pulled_items: 
                item.status = INGREDIENTS_READY_TO_PROCESS
                item.order_id = closest_order.order_id
                item.product_designation = product.product_id  # Set the product designation
                self.inventory.add(item)
                # add the pulled items to the station queue
                if item.product_type == self.product_x:
                    station = self.stations[0]
                    processing_time = station.add_to_queue(item)
                elif item.product_type == self.product_y:
                    station = self.stations[1]
                    processing_time = station.add_to_queue(item)
                elif item.product_type == self.product_z:  # product z can only be processed after product x and y
                    station = self.stations[2]
                    processing_time = station.add_to_queue([item])
                if item.order_id not in self.processing_time_per_order:
                    self.processing_time_per_order[item.order_id] = {}
                self.processing_time_per_order[item.order_id][station.station_id] = processing_time
                print(f"Adding {item} to station {station.station_id} queue.")
    

    def total_orders_count(self) -> None:
        orders = {}
        for customer in self.customers:
            for order in customer.orders:
                for product_type, quantity in order.products:
                    if product_type.product_id not in orders:
                        orders[product_type.product_id] = 0
                    orders[product_type.product_id] += quantity
        print(f"Total orders count: {json.dumps(orders, indent=4)}")


    def start_day(self, temp_data: dict) -> None:
        """
        Prepare the simulation for a new day.
        """
        print(f"Day {self.time}: Starting production cycle.")
        self.init_customer_order_for_day()
        self.receive_supplier_orders()
        needed_ingredients , closest_lead_time , cheapest_supplier = self.order_missing_components_to_produce() if self.ordering_strategy == DEMAND_ONLY else self.order_missing_components_to_produce_by_eoq()
        closest_order = self.get_closest_order(False)
        closest_lead_time = closest_order.due_time if closest_order else None
        self.total_orders_count()
        self.fine_all_delayed_orders()
        self.register_demand(self.product_one, self.get_demand_for_product(self.product_one))
        self.register_demand(self.product_two, self.get_demand_for_product(self.product_two))

        # self.total_income -= self.inventory.calculate_holding_cost()
        # self.get_demand_for_product(self.product_one)
        # self.get_demand_for_product(self.product_two)
        # save the related data to the temp_data dictionary
        temp_data[DAY_KEY] = self.time
        temp_data[CUSTOMER_ORDERS_KEY] = [customer.to_dict() for customer in self.customers]
        temp_data[SUPPLIER_ORDERS_KEY] = [supplier.to_dict() for supplier in self.suppliers]
        temp_data[NEEDED_INGREDIENTS_KEY] = dict(
            needed_ingredients=[(product.to_dict(), quantity) for product, quantity in needed_ingredients],
            closest_lead_time=closest_lead_time,
            cheapest_supplier=cheapest_supplier.to_dict() if cheapest_supplier else None
        )
        temp_data[CLOSEST_ORDER_KEY] = closest_order.to_dict() if closest_order else None
        temp_data[TYPE_TOTAL_INCOME] = self.total_income
        return closest_order, closest_lead_time
    def run_day_processing(self, temp_days_action_data: List[Dict[str, Any]]) -> bool:
        """
        Run the day processing loop.
        """
        STATUS = None
        next_finish_time = None
        while self.current_day_time < WORKING_DAY_LENGTH:
            next_finish_time, station_with_item = self.find_next_station_finished()
            if next_finish_time is None:
                STATUS = 'NO_STATION_PROCESSING'
                break  # No station is currently processing an item
            if self.current_day_time + next_finish_time > WORKING_DAY_LENGTH:
                STATUS = 'NOT_ENOUGH_TIME'
                print(f"Not enough time to process items today. Remaining time: {WORKING_DAY_LENGTH - self.current_day_time}")
                break
            #     # start the processing 
            #     raise ValueError("No station is currently processing an item.")
            print(f"Next station to finish is {station_with_item.station_id} at time {next_finish_time}.")
            # temp_days_action_data.append(dict(
            #     type=TYPE_STATION_PROCESSING_TIME,
            #     current_day_time=self.current_day_time,
            #     stations=[station.to_dict() for station in self.stations],
            #     inventory=self.inventory.to_dict()
            # ))
            self.decrement_time_to_stations(self.current_day_time, next_finish_time, WORKING_DAY_LENGTH)
            self.current_day_time = next_finish_time + self.current_day_time
            # temp_days_action_data.append(dict(
            #     type=TYPE_STATION_PROCESSING_TIME,
            #     current_day_time=self.current_day_time,
            #     stations=[station.to_dict() for station in self.stations],
            #     inventory=self.inventory.to_dict()
            # ))
        print(self.inventory)
        return STATUS, next_finish_time

    def fine_all_delayed_orders(self) -> None:
        """
        Find all orders that are delayed and update their status.
        """
        for customer in self.customers:
            for order in customer.orders:
                if order.due_time < self.time:
                    for product_type, quantity in order.products:
                        product_type.cost = product_type.cost * DAY_FINE_PERCENTAGE
    def producing_by_demand_only(self) -> None:
        """
        Produce products only based on the demand calculated from customer orders.
        This method will be called after initializing the customers and their orders.
        """
        self.json_info[SIMULATION_DAYS_ARRAY_KEY] = []
        # temp_data = {}
        for self.time in range(1,SIMULATION_DAYS + 1):
            self.orders_filled_today = []
            temp_data = dict()
            closest_order, closest_lead_time = self.start_day(temp_data)
            self.sort_stations_by_algorithm()
            temp_data[TYPE_TOTAL_INCOME] = self.total_income
            
            temp_days_action_data = []
            self.current_day_time = 0
            while closest_order is not None :
                print(f'The next closest order is {closest_order} ')
                is_order_in_stock = self.inventory.check_if_order_in_stock(closest_order , )
                # temp_days_action_data.append(dict(
                #     type=TYPE_SET_CLOSEST_ORDER,
                #     current_day_time=self.current_day_time,
                #     closest_order=closest_order.to_dict() if closest_order else None,
                # ))
                print(self.inventory)
                inv_before = self.inventory.to_dict()
                if is_order_in_stock:
                    closest_order, closest_lead_time = self.send_order_in_stock(closest_order)
                    # temp_days_action_data.append(dict(
                    #     type=TYPE_ORDER_IN_STOCK,
                    #     current_day_time=self.current_day_time,
                    #     closest_order=closest_order.to_dict() if closest_order else None,
                    #     inventory_before=inv_before,
                    #     inventory_after=self.inventory.to_dict()
                    # ))
                    continue
                
                has_components_in_stock = self.check_if_components_in_stock(closest_order, )
                if not has_components_in_stock and closest_order.status != INGREDIENTS_READY_TO_PROCESS:
                    # temp_days_action_data.append(dict(
                    #     type=TYPE_COMPONENTS_NOT_IN_STOCK,
                    #     current_day_time=self.current_day_time,
                    #     closest_order=closest_order.to_dict() if closest_order else None,
                    #     inventory_before=inv_before,
                    #     inventory_after=self.inventory.to_dict()
                    # ))
                    closest_order, closest_lead_time = self.handle_no_components_in_stock(closest_order)
                    continue

                # If we have components in stock, we can start producing
                print(closest_order)
                if closest_order is None:
                    print("No orders to fulfill today.")
                    break
                if closest_order.status != INGREDIENTS_READY_TO_PROCESS:
                    self.add_items_from_order_to_station(closest_order)
                    # temp_days_action_data.append(dict(
                    #     type=TYPE_ADD_INGREDIENTS_TO_STATION,
                    #     current_day_time=self.current_day_time,
                    #     closest_order=closest_order.to_dict() if closest_order else None,
                    #     inventory_before=inv_before,
                    #     inventory_after=self.inventory.to_dict()
                    # ))
                
                # check if any order is ready to be fulfilled
                status, _ = self.run_day_processing(temp_days_action_data)
                # next_finish_time, station_with_item = self.find_next_station_finished()
                # temp_days_action_data.append(dict(
                #     type=ORDER_FULFILLED_FROM_WORKING_DAY_START,
                #     current_day_time=self.current_day_time,
                # ))
                closest_order_temp, closest_lead_time_temp = self.fulfill_orders_in_stock(closest_order)
                # temp_days_action_data.append(dict(
                #     type=ORDER_FULFILLED_FROM_WORKING_DAY_END,
                #     current_day_time=self.current_day_time,
                # ))
                if closest_order_temp is not None and closest_lead_time_temp is not None:
                    closest_order = closest_order_temp
                    closest_lead_time = closest_lead_time_temp

                if status == 'NOT_ENOUGH_TIME':
                    print(f"""Not enough time to process items today. Remaining time: {WORKING_DAY_LENGTH - self.current_day_time}
                    Ending 
                          the day and saving the current day ({self.time}).
                    """)
                    break
                    
                if status == 'NO_STATION_PROCESSING' and closest_order is not None:
                    print("No station is currently processing an item. Ending the day.")
                    break
            
            temp_data[TYPE_ORDER_FULFILLED_LIST] = [order.order_id for order in self.orders_filled_today]
            self.json_info[SIMULATION_DAYS_ARRAY_KEY].append(temp_data)
        print('-' * 50)
        print(f"Total income from all orders: {self.total_income}")
        self.json_info[TYPE_PROCESSING_TIME_PER_ORDER] = self.processing_time_per_order
        self.save_json_info()
    def save_json_info(self):
        file = self.generate_file_name()
        import pickle
        with open(f'{file}.pkl', 'wb') as f:
            pickle.dump(self.json_info, f)
            print(f"Simulation data saved to {file}")
        # with open(f'{file}.json', 'w') as f:
        #     json.dump(self.json_info, f)
    def fulfill_orders_in_stock(self, closest_order: Order ) -> None:
        count = 0
        # check for each order if the order is already produced and in stock
        closest_order, closest_lead_time = closest_order, closest_order.due_time
        for customer in self.customers:
            for order in customer.orders:
                is_in_stock = self.inventory.check_if_order_is_produced(order)
                if is_in_stock:
                    count += 1
                    if count > 1:
                        print(f"Order {order.order_id} is already fulfilled and in stock.")
                        
                    self.send_order_in_stock(order , )
                    if closest_order == order:
                        closest_order = self.get_closest_order(False)
                        closest_lead_time = closest_order.due_time if closest_order else None
        return closest_order, closest_lead_time
                    
    def decrement_time_to_stations(self, current_time: float, delta: float , max_time: float) -> None:
        """
        Add time to all stations and process items in the queue.
        first find all the stations that can work and will finish processing in the given time.
        """
        for station in self.stations:
            # check if the station can process items in the queue
            can_processed = station.check_can_be_processed()
            next_finish_time = station.get_next_finish_time()
            if can_processed and current_time + next_finish_time <= max_time:
                station.start_processing()
                item, time = station.decrement_processing_time(0,delta, )
                # add the item to the inventory
                if not item:
                    continue
                print(f"Station {station.station_id} processed item {item} in {time} time units.")
                if item.product_type.product_id == PRODUCT_ID_FIRST or item.product_type.product_id == PRODUCT_ID_SECOND:
                    self.inventory.remove_products_by_designation(item.product_type.product_id, item.order_id)
                    # add the item to the inventory
                    self.inventory.add(item)
                    continue
                
                # check for the item, 
                if item.product_type.product_id != PRODUCT_ID_Z:
                    # add to product z station by the 
                    # find the station where station_id is STATION_THREE_ID
                    station_z = next((s for s in self.stations if s.station_id == STATION_THREE_ID), None)
                    if not station_z:
                        raise ValueError("Station Z not found.")
                    
                    # add to the station_z queue where where the element has the same product_designation as item.product_designation and the same order_id
                    found = False
                    for queue_item in station_z.queue:
                        if queue_item[0][0].product_designation == item.product_designation and queue_item[0][0].order_id == item.order_id:
                            queue_item[0].append(item)
                            found = True
                            break
                    if not found:
                        station_z.queue.append(([item], 0))
                        raise ValueError("Product Z station not found.")
                

    def find_next_station_finished(self) -> Tuple[float | None, Station | None]:
        '''
        The goal is to find the time when the next station will finish processing an item.
        '''
        next_time = math.inf
        station_with_item = None
        for station in self.stations:
            finish_time = station.get_next_finish_time()
            if finish_time < next_time and station.check_can_be_processed():
                next_time = finish_time
                station_with_item = station
        if next_time == math.inf:
            return None , None
        return next_time , station_with_item

    def find_cheapest_supplier(self, product_types: List[Tuple[ProductType, int]], max_lead_time) -> Supplier:
        """
        Find the cheapest supplier for the given product types.
        """
        # Logic to find the cheapest supplier
        # check if We order only from one supplier everything
        cheapest_supplier: Supplier = None
        cost = math.inf
        for supplier in self.suppliers:
            if supplier.lead_time > max_lead_time:
                continue
            total_cost = 0
            for product_type, quantity in product_types:
                cost_unit = supplier.sample_raw_material_cost(product_type)
                total_cost += cost_unit * quantity
            if total_cost < cost:
                cheapest_supplier = supplier
                cost = total_cost
                    
        return cheapest_supplier

    def demand_for_product(self, product_type: ProductType) -> int:
        """
        Calculate the total demand for a specific product type based on customer orders.
        """
        total_demand = 0
        for customer in self.customers:
            for order in customer.orders:
                if order.status != INGREDIENTS_WAITING: # because it either fulfilled or ingredients ordered
                    continue  
                for product_object in order.products:
                    product, quantity = product_object
                    if product == product_type:
                        total_demand += quantity
        return total_demand
    def setup_suppliers(self) -> None:
        """
        Initialize the suppliers for the simulation.
        """
        num_suppliers = random.randint(SUPPLIER_COUNT_MIN, SUPPLIER_COUNT_MAX)
        self.suppliers = [
            Supplier(
                supplier_id=i,
                lead_time=random.randint(SUPPLIER_LEAD_TIME_MIN, SUPPLIER_LEAD_TIME_MAX),
                fixed_order_cost=random.randint(SUPPLIER_ORDER_COST_MIN, SUPPLIER_ORDER_COST_MAX),
                raw_material_cost_distribution={
                    self.product_x: random.randint(*RAW_MATERIAL_COST[PRODUCT_ID_X]),
                    self.product_y: random.randint(*RAW_MATERIAL_COST[PRODUCT_ID_Y]),
                    self.product_z: random.randint(*RAW_MATERIAL_COST[PRODUCT_ID_Z])
                }
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
                max_lead_time=random.randint(CUSTOMER_LEAD_TIME_MIN, CUSTOMER_LEAD_TIME_MAX),
                order_cost=random.randint(CUSTOMER_ORDER_COST_MIN, CUSTOMER_ORDER_COST_MAX)
            ) for i in range(num_customers)
        ]

    def setup_stations(self) -> None:
        """
        Initialize the stations for the simulation.
        """
        station_one = Station(station_id=STATION_ONE_ID)
        station_two = Station(station_id=STATION_TWO_ID)
        station_three = Station(station_id=STATION_THREE_ID)
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
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_FIRST],
            cost=float(random.randint(PRODUCT_A_MIN_PRICE, PRODUCT_A_MAX_PRICE))
        )
        self.product_two = ProductType(
            product_id=PRODUCT_ID_SECOND,
            processing_time_distributions={
                1: 0,  # Station 1
                2: 0,  # Station 2
                3: 0   # Station 3 (custom for product 2)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_SECOND],
            cost=float(random.randint(PRODUCT_B_MIN_PRICE, PRODUCT_B_MAX_PRICE))
        )
        self.product_x = ProductType(
            product_id=PRODUCT_ID_X,
            processing_time_distributions={
                1: max(round(random.expovariate(STATION_PROCESS_TIME[1]), ROUND_DECIMAL_PLACES), MIN_PROCESSING_TIME),  # Station 1
                2: 0,  # Station 2
                3: 0   # Station 3 (custom for product x)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_X],
        )
        self.product_y = ProductType(
            product_id=PRODUCT_ID_Y,
            processing_time_distributions={
                1: 0,  # Station 1
                2: max(round(random.expovariate(STATION_PROCESS_TIME[2]), ROUND_DECIMAL_PLACES), MIN_PROCESSING_TIME),  # Station 2
                3: 0   # Station 3 (custom for product y)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_Y]
        )
        self.product_z = ProductType(
            product_id=PRODUCT_ID_Z,
            processing_time_distributions={
                1: 0,  # Station 1
                2: 0,  # Station 2
                3: max(round(random.expovariate(STATION_PROCESS_TIME[3]), ROUND_DECIMAL_PLACES), MIN_PROCESSING_TIME)  # Station 3 (custom for product z)
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
            ProductInstance(product_type=self.product_x,   order_id=None, amount=random.randint(PRODUCT_X_BASE_INVENTORY_LOW, PRODUCT_X_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_y,   order_id=None, amount=random.randint(PRODUCT_Y_BASE_INVENTORY_LOW, PRODUCT_Y_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_z,   order_id=None, amount=random.randint(PRODUCT_Z_BASE_INVENTORY_LOW, PRODUCT_Z_BASE_INVENTORY_HIGH))
        ])

    def init_customer_order_for_day(self) -> None:
        """
        For each customer, randomly decide whether to place an order for each product type for the day.
        """
        for customer in self.customers:
            # to choose whether to order the first item
            v1 = random.random()
            v2 = random.random()
            q_1 = random.randint(CUSTOMER_MIN_ORDER_QUANTITY, CUSTOMER_MAX_ORDER_QUANTITY)
            q_2 = random.randint(CUSTOMER_MIN_ORDER_QUANTITY, CUSTOMER_MAX_ORDER_QUANTITY)
            if v1 < CUSTOMER_PROBABILITY_TO_ORDER and v2 >= CUSTOMER_PROBABILITY_TO_ORDER:
                customer.place_order([(self.product_one, q_1)], self.time)
            elif v2 < CUSTOMER_PROBABILITY_TO_ORDER and v1 >= CUSTOMER_PROBABILITY_TO_ORDER:
                customer.place_order([(self.product_two, q_2)], self.time)
            elif v2 < CUSTOMER_PROBABILITY_TO_ORDER and v1 < CUSTOMER_PROBABILITY_TO_ORDER:
                customer.place_order([(self.product_one, q_1), (self.product_two, q_2)], self.time)

    def log_statistics(self):
        """Log or print simulation statistics."""
        pass

    def product_tree(self, product_type: ProductType , quantity: int = 1) -> Dict[ProductType, int]:
        """
        Get the ingredients required for each product type.
        Only for product_one and product_two, as they are the main products.
        """
        v = self.v.get(product_type, {})
        ingredients = {}
        for ingredient, amount in v:
            if ingredient not in ingredients:
                ingredients[ingredient] = 0
            ingredients[ingredient] += amount * quantity
        return ingredients

    def get_tree_from_products_list(self, products: List[Tuple[ProductType, int]]) -> Dict[ProductType, int]:
        """
        Get the total ingredients required for a list of product instances.
        """
        total_ingredients = {}
        for product, quantity in products:
            ingredients = self.product_tree(product, quantity)
            for ingredient, amount in ingredients.items():
                if ingredient not in total_ingredients:
                    total_ingredients[ingredient] = 0
                total_ingredients[ingredient] += amount
        return total_ingredients

    def check_if_components_in_stock(self, order: Order, order_id: str | None = None, status: str | None = INGREDIENTS_WAITING) -> bool:
        """
        Check if the ingredients for the order are available.
        Only items that are not related to an order
        """
        needed_ingredients = self.get_tree_from_products_list(order.products)
        
        return self.inventory.has_sufficient_ingredients(needed_ingredients, order_id=order_id, status=status)

    def check_if_ingredients_are_preprocessed(self, station_id: int, amount: int, product_type: ProductType, order_id: int) -> bool:
        """
        This will check if the ingredients for the product are ready to be processed and available in the inventory.
        And the pre-requisites for the product are processed.
        """
        # if STATION_ONE_ID then we check if the inventory have amount of product x, status INGREDIENTS_WAITING
        if station_id == STATION_ONE_ID:
            return self.inventory.has_product_in_status(self.product_x, order_id ,amount, INGREDIENTS_WAITING)
        # elif STATION_TWO_ID then inventory need to have amount of product y, status INGREDIENTS_WAITING
        elif station_id == STATION_TWO_ID:
            return self.inventory.has_product_in_status(self.product_y, amount, INGREDIENTS_WAITING)
        # else then inventory need to have amount  of x , y according to the product_tree function
        else:
            product_tree = self.product_tree(product_type, amount)
            # remove the product z from the product tree
            product_tree.pop(self.product_z, None)
            # check if the inventory has sufficient ingredients for the product tree
            have_x_y = self.inventory.have_amount_in_stock_product_in_order(product_tree, order_id)
            # check for the product z
            have_z = self.inventory.get_product_instances_by_type_and_order(self.product_z, order_id, STATION_ONE_ID) >= amount
            return have_x_y and have_z


    def generate_file_name(self) -> str:
        now = datetime.now()
        # Format as year_month_day_hour_minute_second
        timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
        file_name = f"data/simulation_results_{timestamp}"
        return file_name