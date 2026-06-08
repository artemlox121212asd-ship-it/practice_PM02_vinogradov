SELECT
    g.id AS guest_id,
    g.full_name,
    COUNT(DISTINCT b.id) AS total_bookings,
    COALESCE(SUM(r.price_per_night * DATEDIFF(b.check_out, b.check_in)), 0) AS total_stay_cost,
    COALESCE(SUM(s.price * bs.quantity), 0) AS total_services_cost,
    COALESCE(SUM(r.price_per_night * DATEDIFF(b.check_out, b.check_in)), 0) +
    COALESCE(SUM(s.price * bs.quantity), 0) AS grand_total
FROM Guests g
LEFT JOIN Bookings b ON g.id = b.guest_id
LEFT JOIN Rooms r ON b.room_id = r.id
LEFT JOIN BookingServices bs ON b.id = bs.booking_id
LEFT JOIN Services s ON bs.service_id = s.id
GROUP BY g.id, g.full_name
ORDER BY grand_total DESC;