SELECT AVG(service_total) AS avg_services_per_booking
FROM (
    SELECT bs.booking_id, SUM(s.price * bs.quantity) AS service_total
    FROM BookingServices bs
    JOIN Services s ON bs.service_id = s.id
    GROUP BY bs.booking_id
) AS service_costs;