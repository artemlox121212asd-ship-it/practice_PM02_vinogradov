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