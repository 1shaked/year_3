SELECT 
    I.film_id AS "Film ID"
    ,F.title AS Title
    ,C.customer_id AS "Customer ID"
    ,CONCAT(C.first_name ,' ' ,C.last_name) as "Full Name"
	,COUNT(R.rental_id) AS "Total Rented"

FROM sakila.rental AS R
JOIN sakila.customer AS C ON C.customer_id = R.customer_id
JOIN sakila.inventory as I ON I.inventory_id = R.inventory_id
JOIN sakila.film as F ON F.film_id = I.film_id
GROUP BY I.film_id, C.customer_id

HAVING COUNT(R.rental_id) > 1

ORDER BY COUNT(R.rental_id) DESC

