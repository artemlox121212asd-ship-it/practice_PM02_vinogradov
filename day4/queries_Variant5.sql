USE Hotel;
-- 1. Вывести все записи из главной справочной таблицы
SELECT * FROM guests;

-- 2. Вывести записи, у которых цена > 4000
SELECT * FROM rooms WHERE price_per_night > 4000;

-- 3. Вывести записи, отсортированные по убыванию даты
SELECT * FROM bookings ORDER BY check_in DESC;

-- 4. Вывести записи, где фамилия начинается с буквы 'S'
SELECT * FROM guests WHERE last_name LIKE 'S%';

-- 5. Вывести первые 5 записей из таблицы бронирований
SELECT * FROM bookings LIMIT 5;
-- 6 Вывести связанные данные из двух таблиц
SELECT 
    bookings.id AS booking_id,
    bookings.check_in,
    bookings.status,
    guests.first_name,
    guests.last_name
FROM bookings
JOIN guests ON bookings.guest_id = guests.id;

-- 7 Вывести данные из трёх таблиц
SELECT 
    bookings.id AS booking_id,
    guests.first_name,
    guests.last_name,
    rooms.room_number,
    rooms.room_type,
    rooms.price_per_night
FROM bookings
JOIN guests ON bookings.guest_id = guests.id
JOIN rooms ON bookings.room_id = rooms.id;

-- 8 Вывести левое соединение (LEFT JOIN), чтобы показать даже записи без связей
SELECT 
    guests.first_name,
    guests.last_name,
    bookings.id AS booking_id,
    bookings.status
FROM guests
LEFT JOIN bookings ON guests.id = bookings.guest_id;

-- 9 Вывести список сущностей и количество связанных записей 
SELECT 
    guests.first_name,
    guests.last_name,
    COUNT(bookings.id) AS bookings_count
FROM guests
LEFT JOIN bookings ON guests.id = bookings.guest_id
GROUP BY guests.id;

-- 10 Вывести записи, у которых нет связанных данных 
SELECT 
    guests.first_name,
    guests.last_name
FROM guests
LEFT JOIN bookings ON guests.id = bookings.guest_id
WHERE bookings.id IS NULL;
-- 11 Подсчитать общее количество записей в таблице бронирований
SELECT COUNT(*) AS total_bookings FROM bookings;

-- 12 Вывести сумму, минимум, максимум, среднее по числовому полю
SELECT 
    SUM(price_per_night) AS total_price,
    MIN(price_per_night) AS min_price,
    MAX(price_per_night) AS max_price,
    AVG(price_per_night) AS avg_price
FROM rooms;

-- 13 Сгруппировать данные по одному полю и посчитать количество
SELECT 
    check_in AS booking_date,
    COUNT(*) AS bookings_count
FROM bookings
GROUP BY check_in;

-- 14 Сгруппировать с HAVING
SELECT 
    check_in AS booking_date,
    COUNT(*) AS bookings_count
FROM bookings
GROUP BY check_in
HAVING COUNT(*) > 1;

-- 15 Вывести записи, где значение поля равно максимальному 
SELECT 
    room_number,
    room_type,
    price_per_night
FROM rooms
WHERE price_per_night = (SELECT MAX(price_per_night) FROM rooms);

-- 16 Вывести записи, которых НЕТ в связанной таблице
SELECT * FROM guests
WHERE id NOT IN (SELECT DISTINCT guest_id FROM bookings WHERE guest_id IS NOT NULL);

-- 17 Вывести с использованием EXISTS 
SELECT * FROM guests g
WHERE EXISTS (SELECT 1 FROM bookings b WHERE b.guest_id = g.id);

-- 18 Обновить одно поле у всех записей, удовлетворяющих условию
UPDATE rooms
SET price_per_night = price_per_night * 1.10
WHERE room_type = 'Lux';

-- 19 Обновить запись по id
UPDATE bookings
SET status = 'Cancelled'
WHERE id = 3;

-- 20 Удалить все «устаревшие» записи, где дата < '2020-01-01'
DELETE FROM bookings
WHERE check_out < '2020-01-01';