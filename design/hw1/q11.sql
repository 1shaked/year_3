SELECT DISTINCT 
	C.customer_id
    ,CONCAT(C.first_name, ' ', C.last_name) AS "Customer Name"
FROM 
	customer AS C
JOIN rental AS R ON C.customer_id = R.customer_id
JOIN inventory I ON R.inventory_id = I.inventory_id
JOIN film AS F ON I.film_id = F.film_id
WHERE F.rating IN ('R', 'NC-17');
