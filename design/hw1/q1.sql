
WITH rental_count AS (

SELECT  
	I.film_id AS Film_ID
    ,F.title AS Title
    ,I.store_id AS Store_ID
    ,DATE_FORMAT(R.rental_date, '%Y-%m') AS "Date"
    ,COUNT(R.rental_id) AS Total_Rental
FROM sakila.rental AS R
JOIN sakila.inventory AS I ON (
    I.inventory_id = R.inventory_id
)
JOIN sakila.film AS F ON (
   F.film_id = I.film_id
)
GROUP BY DATE_FORMAT(R.rental_date, '%Y-%m')
        ,I.store_id
        ,I.film_id


ORDER BY COUNT(R.rental_id) DESC
)

SELECT 
	* 
FROM 
	rental_count as R
WHERE R.Total_Rental = (
	SELECT 
		MAX(RI.Total_Rental) 
	FROM 
			rental_count AS RI
	WHERE R.Store_ID = RI.Store_ID 
		AND R.Date = RI.Date
	)
;