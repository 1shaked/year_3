import math
import random
from typing import Dict, List, Optional, Any, Tuple
from itertools import combinations
from consts import *
from entities import INGREDIENTS_WAITING, Order, ProductType, Supplier, Station, ProductInstance, Customer
# =====================
# Simulation Constants
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
            if item.product_type == product_instance.product_type and item.order_id == product_instance.order_id and item.status == product_instance.status:
                item.amount += product_instance.amount
                self.calculate_total_volume()
                return
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

    def check_capacity_for_product(self, product: ProductType, quantity: int) -> bool:
        """Check if there is enough of a product in the stock"""
        return self.get_product_instances_by_type(product) >= quantity
    
    

    # def get_tree_from_products_list(self, products: List[Tuple[ProductType, int]]) -> Dict[ProductType, int]:
    #     """
    #     Get the total ingredients required for a list of product instances.
    #     """
    #     total_ingredients = {}
    #     for product, quantity in products:
    #         ingredients = self.product_tree(product, quantity)
    #         for ingredient, amount in ingredients.items():
    #             if ingredient not in total_ingredients:
    #                 total_ingredients[ingredient] = 0
    #             total_ingredients[ingredient] += amount
    #     return total_ingredients

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
            if item.product_type == product_type and (order_id is None or item.order_id == order_id) and (status is None or item.status == status):
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

    def pull_resource_from_stock(self, product_type: ProductType, quantity: int, order_id: str | None = None , status=INGREDIENTS_WAITING) -> Optional[ProductInstance]:
        """
        Pull a resource from the stock if available.
        Returns the pulled product instance or None if not enough stock.
        """
        for item in self.items:
            if item.product_type == product_type and item.amount >= quantity and (order_id is None or item.order_id == order_id) and item.status == status:
                item.amount -= quantity
                if item.amount == 0:
                    self.items.remove(item)
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
            if not self.check_if_has_in_stock(product_type, quantity):
                return False
        return True
    
    
class SimulationManager:
    """
    Manages the simulation loop, initializes entities, tracks time and performance.
    """
    def __init__(self):
        self.time : int = 0
        # ...existing code...
        # self.time = 0
        # self.entities = []
        # self.statistics = {}

    def run(self):
        """Run the main simulation loop."""
        pass

    def initialize_entities(self):
        """Initialize all simulation entities (stations, products, etc.)."""
        # initialize the products types
        self.setup_products()
        self.v = {
            self.product_one: {(self.product_x, 1), (self.product_y, 1), (self.product_z, 0.75)},
            self.product_two: {(self.product_x, 1), (self.product_y, 1), (self.product_z, 0.75)},
        }
        self.setup_suppliers()
        self.setup_customers()
        self.simulation_days = SIMULATION_DAYS
        self.setup_stations()
        # create the base inventory for the products
        self.setup_inventory()  # Moved inventory setup here
        # simulation days loop
        self.producing_by_demand_only()

    def get_closest_order_lead_time(self, filter_by_waiting: bool = False) -> float | None:
        due_date = math.inf
        for customer in self.customers:
            order = customer.get_closest_order()
            if order and (order.status == INGREDIENTS_WAITING or not filter_by_waiting):
                due_date = min(due_date, order.due_time)
        return due_date if due_date != math.inf else None
    
    def get_closest_order(self, filter_by_waiting: bool = True) -> Order | None:
        """
        Get the closest order that is not yet fulfilled.
        If filter_by_waiting is True, only consider orders that are waiting.
        """
        due_date = math.inf
        closest_order = None
        for customer in self.customers:
            order = customer.get_closest_order(filter_by_waiting)
            if order and (order.status == INGREDIENTS_WAITING or not filter_by_waiting):
                if order.due_time < due_date:
                    due_date = order.due_time
                    closest_order = order
        return closest_order

    def producing_by_demand_only(self) -> None:
        """
        Produce products only based on the demand calculated from customer orders.
        This method will be called after initializing the customers and their orders.
        """
        for i in range(SIMULATION_DAYS):
            self.time += 1  # Increment the time step for each day
            print(f"Day {self.time}: Starting production cycle.")
            # start by simulation for each day
            # each customer have a CUSTOMER_PROBABILITY_TO_ORDER chance to place an order for each product type
            self.init_customer_order_for_day(self.product_one, self.product_two, i)
            # update the inventory based on the suppliers orders received, (by the due date)
            # TODO: 
            for supplier in self.suppliers:
                for order in supplier.orders:
                    if order['due_time'] == self.time:
                        # add the products to the inventory
                        for product_type, quantity in order['products']:
                            product_instance = ProductInstance(product_type=product_type, order_id=None, amount=quantity)
                            self.inventory.add(product_instance)

            # calculate how much product are needed left to produce to fulfill orders
            stock_one = self.inventory.get_product_instances_by_type(self.product_one)
            stock_two = self.inventory.get_product_instances_by_type(self.product_two)
            demand_one = self.demand_for_product(self.product_one)
            demand_two = self.demand_for_product(self.product_two)
            # calculate how much product are needed to produce
            needed_one = max(0, demand_one - stock_one)
            needed_two = max(0, demand_two - stock_two)
            ingredients = self.get_tree_from_products_list([(self.product_one , needed_one) , (self.product_two, needed_two)])
            # find the cheapest supplier for either the first or second product or both
            # transform the ingredients into a list of product types and their quantities
            
            needed_ingredients = list(ingredients.items())
            closest_lead_time = self.get_closest_order_lead_time()
            cheapest_supplier = None
            count = 0
            while cheapest_supplier is None:
                cheapest_supplier = self.find_cheapest_supplier(needed_ingredients, closest_lead_time + count )
                count += 1
            cheapest_supplier.place_order(needed_ingredients, self.time)
            # producing the products
            # start with the closest order
            closest_lead_time = self.get_closest_order_lead_time(False)
            closest_order = self.get_closest_order(False)
            time = 0
            total_money = 0.0
            orders_fulfilled = set()
            while closest_lead_time is not None and time < WORKING_DAY_LENGTH:
                print(closest_order)
                is_order_in_stock = self.inventory.check_if_order_in_stock(closest_order , )
                print(self.inventory)
                if is_order_in_stock:
                    pulled_items = self.inventory.pull_resources_from_stock_by_order(closest_order, status=INGREDIENTS_WAITING)
                    print(pulled_items)
                    closest_order.mark_fulfilled()
                    if closest_order.order_id in orders_fulfilled:
                        raise ValueError(f"Order {closest_order.order_id} is already fulfilled.")
                    orders_fulfilled.add(closest_order.order_id)
                    income = closest_order.calculate_order_cost()
                    total_money += income
                    closest_lead_time = self.get_closest_order_lead_time(True)
                    closest_order = self.get_closest_order(True)
                    continue

                has_components_in_stock = self.check_if_components_in_stock(closest_order, )
                if not has_components_in_stock:
                    print(f"Not enough components in stock to fulfill order {closest_order.order_id}.")
                    closest_order.status = INGREDIENTS_ORDERED
                    # get next closest order
                    closest_lead_time = self.get_closest_order_lead_time(True)
                    closest_order = self.get_closest_order(True)
                    continue

                # If we have components in stock, we can start producing
                print(closest_order)
                components_dict = self.get_tree_from_products_list(closest_order.products)
                pulled_items = self.inventory.pull_resources_from_components_dict(components_dict)
                # TODO: start producing the products
                for product_type, quantity in closest_order.products:
                    # get the ingredients for the product type
                    
                    ingredients = self.product_tree(product_type, quantity)
                    for ingredient, amount in ingredients.items():
                        # process the ingredient on the station
                        product_instance = ProductInstance(product_type=ingredient, order_id=closest_order.order_id, amount=amount)
                        if ingredient == self.product_x:
                            station = self.stations[0]  # Assuming we start with the first station
                        elif ingredient == self.product_y:
                            station = self.stations[1]
                        elif ingredient == self.product_z: #  product z can only be processed after product x and y
                            station = self.stations[2]
                        station.add_to_queue(product_instance)

                    process_times = []
                    # process the next one 
                    # this mean we for each product we check if the station can process it
                    for station in self.stations:
                        for index in range(len(station.queue)):
                            next_in_queue, amount_processes = station.get_item_in_queue(index)
                            can_be_processed = self.check_if_ingredients_are_processed(
                                station.station_id, amount_processes, product_type, next_in_queue.order_id)
                            if not can_be_processed:
                                continue
                            else: 
                                processing_time = station.start_processing(index)
                                
                                process_times.append(processing_time)
                    # check the max processing time, and with that max this is the time we add in the clock and increase the time
                    if process_times:
                        max_processing_time = max(process_times)
                        if max_processing_time + time <= WORKING_DAY_LENGTH:
                            time += max_processing_time
                            # subtract the preprocessed time from all the station processed item
                            for station in self.stations:
                                product, process_time_remain = station.decrement_processing_time_for_working_item(max_processing_time)
                                if product: # this mean add this to the inventory
                                    self.inventory.add(product)
                                    


                    # if max(process_times) + time <= WORKING_DAY_LENGTH:
                    #     time += max(process_times)
                    #     print(f"Processing {quantity} of {product_type.product_id} at stations with times: {process_times}")
                    # else:
                    #     print(f"Not enough time to process {quantity} of {product_type.product_id} today. Remaining time: {WORKING_DAY_LENGTH - time}")
                    #     break


            if closest_lead_time is None:
                print("No orders to fulfill today.")
                continue


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
            
        # TODO: check if we order from multiple suppliers
        
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
            cost=random.randint(PRODUCT_A_MIN_PRICE, PRODUCT_A_MAX_PRICE)
        )
        self.product_two = ProductType(
            product_id=PRODUCT_ID_SECOND,
            processing_time_distributions={
                1: 0,  # Station 1
                2: 0,  # Station 2
                3: 0   # Station 3 (custom for product 2)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_SECOND],
            cost=random.randint(PRODUCT_B_MIN_PRICE, PRODUCT_B_MAX_PRICE)
        )
        self.product_x = ProductType(
            product_id=PRODUCT_ID_X,
            processing_time_distributions={
                1: random.expovariate(STATION_PROCESS_TIME[1]),  # Station 1
                2: 0,  # Station 2
                3: 0   # Station 3 (custom for product x)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_X],
        )
        self.product_y = ProductType(
            product_id=PRODUCT_ID_Y,
            processing_time_distributions={
                1: 0,  # Station 1
                2: random.expovariate(STATION_PROCESS_TIME[2]),  # Station 2
                3: 0   # Station 3 (custom for product y)
            },
            volume_per_unit=PRODUCT_VOLUME[PRODUCT_ID_Y]
        )
        self.product_z = ProductType(
            product_id=PRODUCT_ID_Z,
            processing_time_distributions={
                1: 0,  # Station 1
                2: 0,  # Station 2
                3: random.expovariate(STATION_PROCESS_TIME[3])   # Station 3 (custom for product z)
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
            ProductInstance(product_type=self.product_one, order_id=None, amount=3 * random.randint(PRODUCT_ONE_BASE_INVENTORY_LOW, PRODUCT_ONE_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_two, order_id=None, amount=1 * random.randint(PRODUCT_TWO_BASE_INVENTORY_LOW, PRODUCT_TWO_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_x,   order_id=None, amount=2 * random.randint(PRODUCT_X_BASE_INVENTORY_LOW, PRODUCT_X_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_y,   order_id=None, amount= random.randint(PRODUCT_Y_BASE_INVENTORY_LOW, PRODUCT_Y_BASE_INVENTORY_HIGH)),
            ProductInstance(product_type=self.product_z,   order_id=None, amount= random.randint(PRODUCT_Z_BASE_INVENTORY_LOW, PRODUCT_Z_BASE_INVENTORY_HIGH))
        ])

    def init_customer_order_for_day(self, product_one, product_two, day) -> None:
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
                customer.place_order([(product_one, q_1)], day)
            elif v2 < CUSTOMER_PROBABILITY_TO_ORDER and v1 >= CUSTOMER_PROBABILITY_TO_ORDER:
                customer.place_order([(product_two, q_2)], day)
            elif v2 < CUSTOMER_PROBABILITY_TO_ORDER and v1 < CUSTOMER_PROBABILITY_TO_ORDER:
                customer.place_order([(product_one, q_1), (product_two, q_2)], day)

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
    
    def check_if_ingredients_are_processed(self, station_id: int, amount: int, product_type: ProductType, order_id: int) -> bool:
        """
        This will check if the ingredients for the product are ready to be processed and available in the inventory.
        And the pre-requisites for the product are processed.
        """
        # if STATION_ONE_ID then we check if the inventory have amount of product x, status INGREDIENTS_WAITING
        if station_id == STATION_ONE_ID:
            return self.inventory.has_product_in_status(self.product_x, amount, INGREDIENTS_WAITING)
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