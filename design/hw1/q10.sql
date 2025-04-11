WITH actor_pairs AS (
  SELECT DISTINCT 
	  FA1.actor_id AS actor_id
	  ,FA2.actor_id AS co_actor_id
  FROM film_actor FA1
  JOIN film_actor FA2 ON 
	FA1.film_id = FA2.film_id
	AND FA1.actor_id <> FA2.actor_id
),
co_actor_counts AS (
  SELECT 
    actor_id,
    COUNT(DISTINCT co_actor_id) AS co_actor_count
  FROM actor_pairs
  GROUP BY actor_id
)


SELECT * 
FROM 
	co_actor_counts as C
WHERE 
	C.co_actor_count = (
		SELECT 
			MAX(CI.co_actor_count) 
		FROM 
			co_actor_counts as CI
	)
;
