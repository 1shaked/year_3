SELECT 
    I.film_id AS "Film ID"
    ,F.title AS "Title"
    ,C.customer_id AS "Customer ID"
    ,CONCAT(C.first_name, ' ', C.last_name) as "Full Name"
    ,DATEDIFF( R.return_date , R.rental_date) AS "Rental Duration"
FROM 
	sakila.rental AS R

JOIN sakila.inventory AS I ON I.inventory_id = R.inventory_id

JOIN sakila.film AS F ON F.film_id = I.film_id

JOIN sakila.customer AS C ON C.customer_id = R.customer_id

WHERE DATEDIFF( R.return_date , R.rental_date) = (
	SELECT MAX(DATEDIFF( RI.return_date , RI.rental_date))
    FROM sakila.rental AS RI
)
    
;