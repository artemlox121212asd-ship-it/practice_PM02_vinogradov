SELECT g.*
FROM Guests g
WHERE NOT EXISTS (
    SELECT 1 FROM Bookings b
    JOIN BookingServices bs ON b.id = bs.booking_id
    WHERE b.guest_id = g.id
);