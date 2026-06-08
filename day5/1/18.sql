SELECT r.room_type,
       SUM(DATEDIFF(b.check_out, b.check_in)) AS total_nights_booked
FROM Rooms r
JOIN Bookings b ON r.id = b.room_id
GROUP BY r.room_type
ORDER BY total_nights_booked DESC;