WITH store_monthly_revenue AS (
  SELECT 
    s.store_id,
    DATE_FORMAT(p.payment_date, '%Y-%m') AS revenue_month,
    SUM(p.amount) AS total_revenue
  FROM payment p
  JOIN rental r ON p.rental_id = r.rental_id
  JOIN inventory i ON r.inventory_id = i.inventory_id
  JOIN store s ON i.store_id = s.store_id
  GROUP BY s.store_id, DATE_FORMAT(p.payment_date, '%Y-%m')
),
ranked_revenue AS (
  SELECT *,
         RANK() OVER (PARTITION BY store_id ORDER BY total_revenue DESC) AS revenue_rank
  FROM store_monthly_revenue
)
SELECT 
  store_id,
  revenue_month,
  total_revenue
FROM ranked_revenue
WHERE revenue_rank = 1;
