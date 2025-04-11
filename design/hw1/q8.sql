WITH customer_monthly_rentals AS (
  SELECT 
    customer_id,
    DATE_FORMAT(rental_date, '%Y-%m') AS rental_month,
    COUNT(*) AS rental_count
  FROM rental
  GROUP BY customer_id, DATE_FORMAT(rental_date, '%Y-%m')
)

SELECT 
    customer_id
    ,MAX(rental_count) AS max_rentals
    ,MIN(rental_count) AS min_rentals
    ,ROUND(MAX(rental_count) / NULLIF(MIN(rental_count), 0), 2) AS rental_ratio
	
    
    FROM customer_monthly_rentals
  
	GROUP BY customer_id

	HAVING MAX(rental_count) / NULLIF(MIN(rental_count), 0) >= 3;



