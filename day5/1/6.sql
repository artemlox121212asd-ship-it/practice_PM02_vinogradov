CREATE TABLE BookingServices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    service_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES Services(id) ON DELETE CASCADE
);