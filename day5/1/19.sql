SELECT YEAR(check_in) AS year, MONTH(check_in) AS month, COUNT(*) AS bookings_count
FROM Bookings
GROUP BY YEAR(check_in), MONTH(check_in)
ORDER BY year, month;