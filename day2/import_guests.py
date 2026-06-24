import mysql.connector
import json

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ваш_пароль",
    database="HotelDB"
)
cursor = conn.cursor()

with open('Гости.json', 'r', encoding='utf-8') as file:
    guests = json.load(file)
for guest in guests:
    sql = "INSERT INTO Гости (фамилия, имя, отчество, паспорт, телефон, email) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (guest['фамилия'], guest['имя'], guest.get('отчество', ''), guest['паспорт'], guest.get('телефон', ''), guest.get('email', ''))
    cursor.execute(sql, values)
print(f"Импортировано {len(guests)} гостей")

with open('Номера.json', 'r', encoding='utf-8') as file:
    rooms = json.load(file)
for room in rooms:
    sql = "INSERT INTO Номера (номер_комнаты, тип, цена_за_сутки, вместимость, статус) VALUES (%s, %s, %s, %s, %s)"
    values = (room['номер_комнаты'], room['тип'], room['цена_за_сутки'], room['вместимость'], room['статус'])
    cursor.execute(sql, values)
print(f"Импортировано {len(rooms)} номеров")

with open('Услуги.json', 'r', encoding='utf-8') as file:
    services = json.load(file)
for service in services:
    sql = "INSERT INTO Услуги (название, цена, ед_изм) VALUES (%s, %s, %s)"
    values = (service['название'], service['цена'], service['ед_изм'])
    cursor.execute(sql, values)
print(f"Импортировано {len(services)} услуг")

with open('Бронирования.json', 'r', encoding='utf-8') as file:
    bookings = json.load(file)
for booking in bookings:
    sql = "INSERT INTO Бронирования (id_гостя, id_номера, дата_заезда, дата_выезда, статус) VALUES (%s, %s, %s, %s, %s)"
    values = (booking['id_гостя'], booking['id_номера'], booking['дата_заезда'], booking['дата_выезда'], booking['статус'])
    cursor.execute(sql, values)
print(f"Импортировано {len(bookings)} бронирований")

with open('Бронирования_Услуги.json', 'r', encoding='utf-8') as file:
    booking_services = json.load(file)
for bs in booking_services:
    sql = "INSERT INTO Бронирования_Услуги (id_гостя, id_номера, дата_заезда, id_услуги, количество) VALUES (%s, %s, %s, %s, %s)"
    values = (bs['id_гостя'], bs['id_номера'], bs['дата_заезда'], bs['id_услуги'], bs['количество'])
    cursor.execute(sql, values)
print(f"Импортировано {len(booking_services)} записей допуслуг")

conn.commit()
cursor.close()
conn.close()
print("Импорт завершен!")