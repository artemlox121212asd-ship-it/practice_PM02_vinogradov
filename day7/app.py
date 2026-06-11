from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt
from functools import wraps
import random
import os

app = Flask(__name__)
app.secret_key = '7f3e8a2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f'  # В реальном проекте хранить в .env

# Настройки MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'kentyarik123!'  # Ваш пароль от MySQL
app.config['MYSQL_DB'] = 'Hotel_Variant5'  # Имя вашей БД
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# ========== ДЕКОРАТОРЫ ДЛЯ ПРОВЕРКИ ДОСТУПА ==========

def login_required(f):
    """Требует авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Требует роли администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Доступ запрещён. Требуется роль администратора.', 'danger')
            return redirect(url_for('worker_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ========== СТРАНИЦЫ ==========

@app.route('/')
def index():
    """Главная страница"""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('worker_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа с капчей"""
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        captcha_user = request.form['captcha']
        
        # Проверка капчи
        expected = session.get('captcha_result')
        if not captcha_user.isdigit() or int(captcha_user) != expected:
            flash('Неверно введена капча', 'danger')
            return redirect(url_for('login'))
        
        # Поиск пользователя в БД
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Пользователи WHERE логин = %s", (login,))
        user = cur.fetchone()
        cur.close()
        
        if user:
            # Проверка пароля (хешированного)
            stored_hash = user['пароль_hash']
            if stored_hash != 'temp' and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                # Успешный вход
                session['user_id'] = user['id_пользователя']
                session['login'] = user['логин']
                session['role'] = user['роль']
                flash(f'Добро пожаловать, {user["логин"]}!', 'success')
                
                if user['роль'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('worker_dashboard'))
            else:
                flash('Неверный логин или пароль', 'danger')
        else:
            flash('Неверный логин или пароль', 'danger')
    
    # Генерация капчи (простое сложение)
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['captcha_result'] = num1 + num2
    
    return render_template('login.html', num1=num1, num2=num2)


@app.route('/logout')
def logout():
    """Выход из системы"""
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


# ========== ПАНЕЛЬ АДМИНИСТРАТОРА ==========

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Панель администратора"""
    # Получаем статистику из базы отелей
    cur = mysql.connection.cursor()
    
    # Количество гостей
    cur.execute("SELECT COUNT(*) as count FROM Гости")
    guests_count = cur.fetchone()['count']
    
    # Количество бронирований
    cur.execute("SELECT COUNT(*) as count FROM Бронирования")
    bookings_count = cur.fetchone()['count']
    
    # Количество номеров
    cur.execute("SELECT COUNT(*) as count FROM Номера")
    rooms_count = cur.fetchone()['count']
    
    cur.close()
    
    return render_template('admin/dashboard.html', 
                         guests_count=guests_count,
                         bookings_count=bookings_count,
                         rooms_count=rooms_count)


@app.route('/admin/users')
@admin_required
def admin_users():
    """Управление пользователями (только админ)"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_пользователя, логин, роль, created_at FROM Пользователи")
    users = cur.fetchall()
    cur.close()
    return render_template('admin/users.html', users=users)


@app.route('/admin/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Добавление нового пользователя"""
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        role = request.form['role']
        
        # Хеширование пароля
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO Пользователи (логин, пароль_hash, роль) VALUES (%s, %s, %s)",
                (login, hashed.decode('utf-8'), role)
            )
            mysql.connection.commit()
            flash(f'Пользователь {login} успешно создан', 'success')
        except Exception as e:
            flash(f'Ошибка: пользователь с таким логином уже существует', 'danger')
        finally:
            cur.close()
        
        return redirect(url_for('admin_users'))
    
    return render_template('admin/add_user.html')


@app.route('/admin/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    """Удаление пользователя"""
    # Нельзя удалить самого себя
    if user_id == session['user_id']:
        flash('Нельзя удалить самого себя', 'danger')
        return redirect(url_for('admin_users'))
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Пользователи WHERE id_пользователя = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Пользователь удалён', 'success')
    return redirect(url_for('admin_users'))


# ========== ПАНЕЛЬ РАБОТНИКА ==========

@app.route('/worker/dashboard')
@login_required
def worker_dashboard():
    """Панель работника"""
    cur = mysql.connection.cursor()
    
    # Получаем список активных бронирований
    cur.execute("""
        SELECT б.id_бронирования, г.фамилия, г.имя, н.тип as номер_тип,
               б.дата_заезда, б.дата_выезда, б.статус
        FROM Бронирования б
        JOIN Гости г ON б.id_гостя = г.id_гостя
        JOIN Номера н ON б.id_номера = н.id_номера
        ORDER BY б.дата_заезда DESC
        LIMIT 10
    """)
    bookings = cur.fetchall()
    cur.close()
    
    return render_template('worker/dashboard.html', bookings=bookings)



# ========== УПРАВЛЕНИЕ ЗАКАЗАМИ (БРОНИРОВАНИЯМИ) ==========

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    """Управление бронированиями для администратора"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT б.*, г.фамилия, г.имя, г.отчество, н.тип as тип_номера
        FROM Бронирования б
        JOIN Гости г ON б.id_гостя = г.id_гостя
        JOIN Номера н ON б.id_номера = н.id_номера
        ORDER BY б.дата_заезда DESC
    """)
    bookings = cur.fetchall()
    cur.close()
    return render_template('admin/bookings.html', bookings=bookings)


@app.route('/worker/bookings')
@login_required
def worker_bookings():
    """Просмотр бронирований для работника"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT б.id_бронирования, г.фамилия, г.имя, н.тип as тип_номера,
               б.дата_заезда, б.дата_выезда, б.статус
        FROM Бронирования б
        JOIN Гости г ON б.id_гостя = г.id_гостя
        JOIN Номера н ON б.id_номера = н.id_номера
        ORDER BY б.дата_заезда DESC
    """)
    bookings = cur.fetchall()
    cur.close()
    return render_template('worker/bookings.html', bookings=bookings)


@app.route('/booking/update_status/<int:booking_id>', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    """Обновление статуса бронирования"""
    new_status = request.form.get('status')
    
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE Бронирования SET статус = %s WHERE id_бронирования = %s",
        (new_status, booking_id)
    )
    mysql.connection.commit()
    cur.close()
    
    flash('Статус бронирования обновлён', 'success')
    
    # Возвращаемся на нужную панель
    if session.get('role') == 'admin':
        return redirect(url_for('admin_bookings'))
    else:
        return redirect(url_for('worker_bookings'))


@app.route('/booking/delete/<int:booking_id>')
@admin_required
def delete_booking(booking_id):
    """Удаление бронирования (только админ)"""
    if not messagebox_confirm:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Бронирования WHERE id_бронирования = %s", (booking_id,))
        mysql.connection.commit()
        cur.close()
        flash('Бронирование удалено', 'success')
    
    return redirect(url_for('admin_bookings'))


# Вспомогательная функция для подтверждения (простая версия)
def messagebox_confirm():
    """Имитация подтверждения (можно заменить на модальное окно)"""
    return True
# ========== ЗАПУСК ==========

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)