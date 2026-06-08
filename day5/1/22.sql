INSERT INTO Bookings (guest_id, room_id, check_in, check_out, status) VALUES
(1, 4, '2025-08-01', '2025-08-03', 'cancelled');

INSERT INTO BookingServices (booking_id, service_id, quantity) VALUES
(LAST_INSERT_ID(), 1, 2);

DELETE FROM BookingServices WHERE booking_id IN (SELECT id FROM (SELECT id FROM Bookings WHERE status = 'cancelled') AS tmp);
DELETE FROM Bookings WHERE status = 'cancelled';

SELECT * FROM Bookings;