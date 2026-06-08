SELECT id, full_name, passport, phone
FROM Guests
ORDER BY SUBSTRING_INDEX(full_name, ' ', -1);