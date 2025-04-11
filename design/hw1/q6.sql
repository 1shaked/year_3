WITH monthly_rent AS (

	SELECT
		COUNT(R.rental_id) as count_rent
		,DATE_FORMAT(R.rental_date, '%Y-%m') AS month_rented
        ,MIN(R.rental_date) as min_date
		
	FROM sakila.rental AS R

	GROUP BY DATE_FORMAT(R.rental_date, '%Y-%m')

	ORDER BY MIN(R.rental_date)
)

SELECT 
	M.month_rented AS "DATE Rented"
    ,M.count_rent - LAG(M.count_rent) over (ORDER BY M.min_date) AS "Drop Rate"
	#,LAG(M.count_rent) over (ORDER BY M.min_date AS "Previous month"
FROM 
	monthly_rent as M

ORDER BY M.count_rent - LAG(M.count_rent) over (ORDER BY M.min_date) ASC

LIMIT 2 # need to decide what to do with the first month
;

