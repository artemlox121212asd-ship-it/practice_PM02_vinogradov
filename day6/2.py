import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error

# Глобальная переменная для пароля
DB_PASSWORD = None

def get_password():
    """Запрашивает пароль у пользователя"""
    global DB_PASSWORD
    if DB_PASSWORD is None:
        root = tk.Tk()
        root.withdraw()
        DB_PASSWORD = simpledialog.askstring("Пароль MySQL", 
                                            "Введите пароль для пользователя root:", 
                                            show='*')
        root.destroy()
        if DB_PASSWORD is None:
            messagebox.showerror("Ошибка", "Пароль не введен! Приложение будет закрыто.")
            exit()
    return DB_PASSWORD

def connect_db():
    """Подключение к базе данных MySQL"""
    try:
        password = get_password()
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,
            database="hotel_variant5"
        )
        return connection
    except Error as e:
        global DB_PASSWORD
        DB_PASSWORD = None  # Сбрасываем пароль при ошибке
        messagebox.showerror("Ошибка БД", f"Не удалось подключиться: {e}")
        return None


class DatabaseApp:
    """Основной класс приложения для работы с таблицей БД"""
    
    def __init__(self, root, table_name, columns):
        """
        table_name: имя таблицы (например, 'Гости')
        columns: список словарей с описанием столбцов
        """
        self.root = root
        self.table_name = table_name
        self.columns = columns
        
        self.root.title(f"🏨 Управление таблицей: {table_name}")
        self.root.geometry("900x550")
        self.root.resizable(True, True)
        
        # Создаём интерфейс
        self.create_widgets()
        
        # Загружаем данные
        self.refresh_table()
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        
        # ========== Рамка для полей ввода ==========
        input_frame = tk.LabelFrame(self.root, text="📝 Данные записи", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.entries = {}
        row = 0
        col = 0
        
        # Создаём поля для каждого столбца (кроме автогенерируемого PK)
        for col_config in self.columns:
            # Пропускаем PK с AUTO_INCREMENT
            if col_config.get('pk') and col_config.get('auto_increment'):
                continue
            
            # Метка
            label = tk.Label(input_frame, text=f"{col_config['label']}:", 
                           font=('Arial', 10, 'bold'))
            label.grid(row=row, column=col*2, padx=5, pady=5, sticky="e")
            
            # Поле ввода
            entry = tk.Entry(input_frame, width=25, font=('Arial', 10))
            entry.grid(row=row, column=col*2+1, padx=5, pady=5)
            self.entries[col_config['name']] = entry
            
            col += 1
            if col >= 3:  # 3 поля в строке
                col = 0
                row += 1
        
        # ========== Кнопки действий ==========
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        buttons = [
            ("➕ Добавить", "#90EE90", self.add_record),
            ("✏️ Обновить", "#FFD700", self.update_record),
            ("🗑️ Удалить", "#FF6347", self.delete_record),
            ("🧹 Очистить", "#D3D3D3", self.clear_entries),
            ("🔄 Обновить", "#87CEEB", self.refresh_table),
        ]
        
        for i, (text, color, command) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, bg=color, width=12,
                           font=('Arial', 9, 'bold'), command=command)
            btn.grid(row=0, column=i, padx=5)
        
        # ========== Строка поиска ==========
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5, fill=tk.X, padx=10)
        
        tk.Label(search_frame, text="🔍 Поиск:", font=('Arial', 10)).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=40, font=('Arial', 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Найти", command=self.search, 
                 bg="#E0E0E0", width=10).pack(side=tk.LEFT)
        
        # ========== Таблица Treeview ==========
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаём скролл
        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Определяем колонки для Treeview
        columns_display = [col['name'] for col in self.columns]
        
        self.tree = ttk.Treeview(tree_frame, columns=columns_display, show="headings",
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Настраиваем заголовки и ширину колонок
        for col in self.columns:
            self.tree.heading(col['name'], text=col['label'])
            # Задаём ширину в зависимости от типа
            width = 80 if col.get('pk') else 120
            if col['label'] == 'Паспорт':
                width = 130
            elif col['label'] == 'Телефон':
                width = 120
            self.tree.column(col['name'], width=width, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Привязываем событие выбора строки
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # ========== Статусная строка ==========
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def refresh_table(self):
        """Обновить данные в таблице Treeview"""
        # Очищаем текущие данные
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Получаем данные из БД
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name}"
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            self.status_var.set(f"✅ Загружено {len(rows)} записей")
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            self.status_var.set("❌ Ошибка загрузки данных")
        finally:
            cursor.close()
            conn.close()
    
    def on_select(self, event):
        """При выборе строки в таблице — заполняем поля ввода"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        
        # Заполняем поля ввода
        for i, col in enumerate(self.columns):
            col_name = col['name']
            if col_name in self.entries:
                self.entries[col_name].delete(0, tk.END)
                if values[i] is not None:
                    self.entries[col_name].insert(0, str(values[i]))
        
        self.status_var.set("📋 Выбрана запись для редактирования")
    
    def get_pk_name(self):
        """Вернуть имя первичного ключа"""
        for col in self.columns:
            if col.get('pk'):
                return col['name']
        return None
    
    def get_pk_value_from_selected(self):
        """Получить значение PK из выбранной строки"""
        selected = self.tree.selection()
        if not selected:
            return None
        
        values = self.tree.item(selected[0])['values']
        pk_name = self.get_pk_name()
        if not pk_name:
            return None
        
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        return values[pk_index]
    
    def add_record(self):
        """Добавить новую запись"""
        # Собираем значения из полей ввода
        values = {}
        for col_name, entry in self.entries.items():
            values[col_name] = entry.get().strip()
        
        # Проверяем обязательные поля
        for col in self.columns:
            col_name = col['name']
            if col.get('required') and col_name in self.entries and not values[col_name]:
                messagebox.showwarning("Ошибка", f"Поле '{col['label']}' обязательно для заполнения")
                return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        columns_names = list(values.keys())
        placeholders = ", ".join(["%s"] * len(columns_names))
        query = f"INSERT INTO {self.table_name} ({', '.join(columns_names)}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, list(values.values()))
            conn.commit()
            messagebox.showinfo("Успех", "✅ Запись добавлена")
            self.clear_entries()
            self.refresh_table()
            self.status_var.set("✅ Запись успешно добавлена")
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
            self.status_var.set("❌ Ошибка при добавлении")
        finally:
            cursor.close()
            conn.close()
    
    def update_record(self):
        """Обновить выбранную запись"""
        pk_value = self.get_pk_value_from_selected()
        if not pk_value:
            messagebox.showwarning("Предупреждение", "Выберите запись для обновления")
            return
        
        # Собираем новые значения из полей
        new_values = {}
        for col_name, entry in self.entries.items():
            new_values[col_name] = entry.get().strip()
        
        if not new_values:
            messagebox.showwarning("Предупреждение", "Нет данных для обновления")
            return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        pk_name = self.get_pk_name()
        set_clause = ", ".join([f"{col} = %s" for col in new_values.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_name} = %s"
        
        try:
            params = list(new_values.values()) + [pk_value]
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Успех", "✏️ Запись обновлена")
            self.refresh_table()
            self.status_var.set("✅ Запись успешно обновлена")
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
            self.status_var.set("❌ Ошибка при обновлении")
        finally:
            cursor.close()
            conn.close()
    
    def delete_record(self):
        """Удалить выбранную запись"""
        pk_value = self.get_pk_value_from_selected()
        if not pk_value:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить запись?\nЭто действие нельзя отменить!"):
            return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        pk_name = self.get_pk_name()
        query = f"DELETE FROM {self.table_name} WHERE {pk_name} = %s"
        
        try:
            cursor.execute(query, (pk_value,))
            conn.commit()
            messagebox.showinfo("Успех", "🗑️ Запись удалена")
            self.clear_entries()
            self.refresh_table()
            self.status_var.set("✅ Запись успешно удалена")
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
            self.status_var.set("❌ Ошибка при удалении")
        finally:
            cursor.close()
            conn.close()
    
    def clear_entries(self):
        """Очистить все поля ввода"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.status_var.set("🧹 Поля ввода очищены")
    
    def search(self):
        """Поиск по таблице"""
        keyword = self.search_entry.get().strip()
        
        if not keyword:
            self.refresh_table()
            return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        # Получаем все текстовые поля (не PK)
        text_columns = [col['name'] for col in self.columns 
                       if not col.get('pk')]
        
        if not text_columns:
            self.refresh_table()
            return
        
        conditions = " OR ".join([f"{col} LIKE %s" for col in text_columns])
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"
        
        try:
            cursor.execute(query, tuple([f"%{keyword}%"] * len(text_columns)))
            rows = cursor.fetchall()
            
            # Очищаем таблицу
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            # Заполняем результатами поиска
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            
            self.status_var.set(f"🔍 Найдено {len(rows)} записей по запросу '{keyword}'")
        except Error as e:
            messagebox.showerror("Ошибка", str(e))
            self.status_var.set("❌ Ошибка поиска")
        finally:
            cursor.close()
            conn.close()


def main():
    """Главная функция запуска приложения"""
    root = tk.Tk()
    
    # Конфигурация для таблицы "Гости" (из варианта 5)
    columns = [
        {"name": "id_гостя", "label": "ID", "pk": True, "auto_increment": True},
        {"name": "фамилия", "label": "Фамилия", "required": True},
        {"name": "имя", "label": "Имя", "required": True},
        {"name": "отчество", "label": "Отчество", "required": False},
        {"name": "паспорт", "label": "Паспорт", "required": True},
        {"name": "телефон", "label": "Телефон", "required": False},
    ]
    
    app = DatabaseApp(root, table_name="Гости", columns=columns)
    root.mainloop()


if __name__ == "__main__":
    main()