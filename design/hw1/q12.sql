WITH customer_months AS (
  SELECT DISTINCT
    customer_id,
    DATE_FORMAT(rental_date, '%Y-%m') AS rental_month,
    DATE_FORMAT(rental_date, '%Y-%m-01') AS rental_month_start
  FROM rental
),
numbered_months AS (
  SELECT 
    customer_id,
    rental_month,
    rental_month_start,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY rental_month_start) AS row_num
  FROM customer_months
),
streaks AS (
  SELECT 
    customer_id,
    DATE_SUB(rental_month_start, INTERVAL row_num MONTH) AS streak_group
  FROM numbered_months
),
streak_lengths AS (
  SELECT 
    customer_id,
    COUNT(*) AS streak_length
  FROM streaks
  GROUP BY customer_id, streak_group
),
max_streaks AS (
  SELECT 
    customer_id,
    MAX(streak_length) AS max_streak
  FROM streak_lengths
  GROUP BY customer_id
),
top_streak AS (
  SELECT MAX(max_streak) AS longest_streak FROM max_streaks
)
SELECT 
  c.customer_id,
  CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
  m.max_streak
FROM max_streaks m
JOIN customer c ON c.customer_id = m.customer_id
JOIN top_streak t ON m.max_streak = t.longest_streak;
