SELECT b.id AS booking_id,
       g.full_name,
       r.room_number,
       DATEDIFF(b.check_out, b.check_in) AS nights,
       r.price_per_night * DATEDIFF(b.check_out, b.check_in) AS stay_cost
FROM Bookings b
JOIN Guests g ON b.guest_id = g.id
JOIN Rooms r ON b.room_id = r.id
ORDER BY b.id;