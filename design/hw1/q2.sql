SELECT 
    F.film_id,
    F.title
FROM sakila.film AS F
LEFT JOIN sakila.inventory AS I ON F.film_id = I.film_id
LEFT JOIN sakila.rental AS R ON I.inventory_id = R.inventory_id
WHERE R.rental_id IS NULL
GROUP BY F.film_id, F.title;
