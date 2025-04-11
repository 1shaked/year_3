SELECT 
	P.customer_id AS "Customer ID"
    ,CONCAT(C.first_name, ' ', C.last_name) as "Full Name"
    ,SUM(p.amount) AS "TOTAL SPENT"
FROM 
	sakila.payment AS P
JOIN sakila.customer AS C ON C.customer_id = P.customer_id

GROUP BY P.customer_id    
	# CONCAT(C.first_name, ' ', C.last_name) # Adding this is not mendatory but usally is added for saftey resaon 

HAVING SUM(p.amount) > 1.5 * (
		SELECT AVG(PI.amount)
        FROM sakila.payment AS PI
	)
    

;