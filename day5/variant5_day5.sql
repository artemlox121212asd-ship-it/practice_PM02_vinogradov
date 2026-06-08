-- ======================================================
-- ДЕНЬ 5. Самостоятельная работа: SQL-запросы
-- Вариант 5. Гостиница
-- Студент: Виноградов Андрей
-- Группа: 24 ИС
-- ======================================================

SET SQL_SAFE_UPDATES = 0;

-- Задание 1. Создать БД, таблицы
DROP DATABASE IF EXISTS Variant5_Work;
CREATE DATABASE Variant5_Work;
USE Variant5_Work;

-- Задание 2. Rooms: номер, тип, цена_за_сутки, вместимость
CREATE TABLE Rooms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    room_type VARCHAR(50) NOT NULL,
    price_per_night DECIMAL(10,2) NOT NULL,
    capacity INT NOT NULL
);

-- Задание 3. Guests: ФИО, паспорт, телефон
CREATE TABLE Guests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(150) NOT NULL,
    passport VARCHAR(20) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL
);

-- Задание 4. Bookings: guest_id, room_id, check_in, check_out, status
CREATE TABLE Bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    guest_id INT NOT NULL,
    room_id INT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status VARCHAR(30) DEFAULT 'active',
    FOREIGN KEY (guest_id) REFERENCES Guests(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Rooms(id) ON DELETE CASCADE
);

-- Задание 5. Services: название, цена
CREATE TABLE Services (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- Задание 6. BookingServices: booking_id, service_id, quantity
CREATE TABLE BookingServices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    service_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES Services(id) ON DELETE CASCADE
);

-- Задание 7. Вставить 5 номеров (люкс, стандарт, эконом и т.д.)
INSERT INTO Rooms (room_number, room_type, price_per_night, capacity) VALUES
('101', 'standart', 2500.00, 2),
('102', 'standart', 2500.00, 2),
('201', 'lux', 5000.00, 3),
('202', 'lux', 5500.00, 4),
('301', 'econom', 1500.00, 1);

-- Задание 8. Вставить 4 гостей
INSERT INTO Guests (full_name, passport, phone) VALUES
('Иванов Иван Иванович', '4510 123456', '+7-900-111-2233'),
('Петрова Мария Сергеевна', '4512 654321', '+7-901-222-3344'),
('Сидоров Алексей Викторович', '4515 987654', '+7-902-333-4455'),
('Козлова Елена Дмитриевна', '4520 112233', '+7-903-444-5566');

-- Задание 9. Вставить 3 услуги (завтрак, уборка, трансфер)
INSERT INTO Services (name, price) VALUES
('Завтрак', 500.00),
('Уборка', 700.00),
('Трансфер', 1500.00);

-- Задание 10. Создать 4 бронирования (разные даты)
INSERT INTO Bookings (guest_id, room_id, check_in, check_out, status) VALUES
(1, 1, '2025-06-10', '2025-06-15', 'active'),
(2, 3, '2025-06-12', '2025-06-18', 'active'),
(3, 5, '2025-05-20', '2025-05-25', 'completed'),
(4, 2, '2025-07-01', '2025-07-05', 'active');

-- Задание 11. Привязать услуги к бронированиям (например, завтрак – 2 дня)
INSERT INTO BookingServices (booking_id, service_id, quantity) VALUES
(1, 1, 5),
(1, 2, 2),
(2, 1, 6),
(2, 3, 1),
(3, 1, 5),
(4, 1, 4);

-- Задание 12. Вывести все свободные номера на текущую дату
SELECT r.*
FROM Rooms r
WHERE NOT EXISTS (
    SELECT 1 FROM Bookings b
    WHERE b.room_id = r.id
      AND b.status = 'active'
      AND b.check_in <= CURDATE()
      AND b.check_out >= CURDATE()
);

-- Задание 13. Вывести список гостей с указанием их бронирований (JOIN)
SELECT g.full_name, g.phone, b.id AS booking_id, r.room_number, b.check_in, b.check_out, b.status
FROM Guests g
JOIN Bookings b ON g.id = b.guest_id
JOIN Rooms r ON b.room_id = r.id
ORDER BY g.full_name, b.check_in;

-- Задание 14. Найти бронирования, у которых дата заезда позже заданной ('2025-05-01')
SELECT * FROM Bookings
WHERE check_in > '2025-05-01';

-- Задание 15. Отсортировать гостей по фамилии
SELECT id, full_name, passport, phone
FROM Guests
ORDER BY SUBSTRING_INDEX(full_name, ' ', -1);

-- Задание 16. Рассчитать стоимость проживания для каждого бронирования
SELECT b.id AS booking_id,
       g.full_name,
       r.room_number,
       DATEDIFF(b.check_out, b.check_in) AS nights,
       r.price_per_night * DATEDIFF(b.check_out, b.check_in) AS stay_cost
FROM Bookings b
JOIN Guests g ON b.guest_id = g.id
JOIN Rooms r ON b.room_id = r.id
ORDER BY b.id;

-- Задание 17. Найти среднюю стоимость дополнительных услуг на одно бронирование
SELECT AVG(service_total) AS avg_services_per_booking
FROM (
    SELECT bs.booking_id, SUM(s.price * bs.quantity) AS service_total
    FROM BookingServices bs
    JOIN Services s ON bs.service_id = s.id
    GROUP BY bs.booking_id
) AS service_costs;

-- Задание 18. Вывести тип номера и общее количество забронированных ночей по этому типу
SELECT r.room_type,
       SUM(DATEDIFF(b.check_out, b.check_in)) AS total_nights_booked
FROM Rooms r
JOIN Bookings b ON r.id = b.room_id
GROUP BY r.room_type
ORDER BY total_nights_booked DESC;

-- Задание 19. Сгруппировать бронирования по месяцам и подсчитать количество
SELECT YEAR(check_in) AS year, MONTH(check_in) AS month, COUNT(*) AS bookings_count
FROM Bookings
GROUP BY YEAR(check_in), MONTH(check_in)
ORDER BY year, month;

-- Задание 20. Найти гостей, которые не заказывали ни одной услуги (NOT EXISTS)
SELECT g.*
FROM Guests g
WHERE NOT EXISTS (
    SELECT 1 FROM Bookings b
    JOIN BookingServices bs ON b.id = bs.booking_id
    WHERE b.guest_id = g.id
);

-- Задание 21. Увеличить цену всех услуг на 15%
UPDATE Services SET price = price * 1.15;
SELECT * FROM Services;

-- Задание 22. Удалить бронирование со статусом «отменено»
INSERT INTO Bookings (guest_id, room_id, check_in, check_out, status) VALUES
(1, 4, '2025-08-01', '2025-08-03', 'cancelled');

INSERT INTO BookingServices (booking_id, service_id, quantity) VALUES
(LAST_INSERT_ID(), 1, 2);

DELETE FROM BookingServices WHERE booking_id IN (SELECT id FROM (SELECT id FROM Bookings WHERE status = 'cancelled') AS tmp);
DELETE FROM Bookings WHERE status = 'cancelled';

SELECT * FROM Bookings;

-- Задание 23. Добавить столбец email в Guests
ALTER TABLE Guests ADD COLUMN email VARCHAR(100);
SELECT * FROM Guests;

-- Задание 24. Создать представление CurrentBookings, показывающее занятые номера сегодня
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

-- Задание 25. Сложный запрос: для каждого гостя вывести общее количество его бронирований, общую сумму за проживание и общую сумму за услуги
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

SET SQL_SAFE_UPDATES = 1;