import bcrypt
import mysql.connector

# Параметры подключения
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kentyarik123!',  # Ваш пароль
    'database': 'Hotel_Variant5'
}

# Пользователи: (логин, пароль, роль)
users = [
    ('admin', 'admin123', 'admin'),
    ('worker', 'worker123', 'worker')
]

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    for login, password, role in users:
        # Хешируем пароль
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Обновляем или вставляем пользователя
        cursor.execute("""
            INSERT INTO Пользователи (логин, пароль_hash, роль) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            пароль_hash = VALUES(пароль_hash), роль = VALUES(роль)
        """, (login, hashed.decode('utf-8'), role))
        
        print(f"✅ Пользователь '{login}' создан/обновлён (пароль: {password})")
    
    conn.commit()
    print("\n🎉 Все пользователи успешно добавлены!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()