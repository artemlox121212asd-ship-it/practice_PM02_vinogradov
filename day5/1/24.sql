CREATE OR REPLACE VIEW CurrentBookings AS
SELECT b.id AS booking_id,
       g.full_name AS guest_name,
       r.room_number,
       b.check_in,
       b.check_out
FROM Bookings b
JOIN Guests g ON b.guest_id = g.id
JOIN Rooms r ON b.room_id = r.id
WHERE b.status = 'active'
  AND b.check_in <= CURDATE()
  AND b.check_out >= CURDATE();

SELECT * FROM CurrentBookings;