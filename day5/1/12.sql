SELECT r.*
FROM Rooms r
WHERE NOT EXISTS (
    SELECT 1 FROM Bookings b
    WHERE b.room_id = r.id
      AND b.status = 'active'
      AND b.check_in <= CURDATE()
      AND b.check_out >= CURDATE()
);