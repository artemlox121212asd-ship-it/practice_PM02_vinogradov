SELECT g.full_name, g.phone, b.id AS booking_id, r.room_number, b.check_in, b.check_out, b.status
FROM Guests g
JOIN Bookings b ON g.id = b.guest_id
JOIN Rooms r ON b.room_id = r.id
ORDER BY g.full_name, b.check_in;