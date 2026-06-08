CREATE TABLE Rooms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    room_type VARCHAR(50) NOT NULL,
    price_per_night DECIMAL(10,2) NOT NULL,
    capacity INT NOT NULL
);