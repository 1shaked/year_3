SELECT 
	R.customer_id
    ,CONCAT(C.first_name, ' ', C.last_name) as "Full Name"
FROM 
	sakila.rental AS R

JOIN 
	sakila.inventory AS I ON 
		I.inventory_id = R.inventory_id

JOIN sakila.film_category AS FC ON
	FC.film_id = I.film_id
    
JOIN sakila.customer AS C ON 
	C.customer_id = R.customer_id


GROUP BY R.customer_id 
     ,CONCAT(C.first_name, ' ', C.last_name) # This just to display the full name in our case it is not mandatory but just to be sure.
HAVING COUNT(DISTINCT FC.category_id) = (
		SELECT COUNT(*)
        FROM sakila.category 
	)
