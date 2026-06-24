#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta

from repositories.in_memory import (
    InMemoryBoardRepository,
    InMemoryColumnRepository,
    InMemoryTaskRepository,
    InMemoryTagRepository,
    InMemoryHistoryRepository
)
from services.task_service import TaskManagerService
from services.schemas import BoardCreate, ColumnCreate, TaskCreate, TagCreate
from domain.exceptions import TaskNotFoundError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    # 1. Создаём репозитории (In-Memory)
    board_repo = InMemoryBoardRepository()
    column_repo = InMemoryColumnRepository()
    task_repo = InMemoryTaskRepository()
    tag_repo = InMemoryTagRepository()
    history_repo = InMemoryHistoryRepository()

    # 2. Создаём сервис с внедрением зависимостей (DI)
    service = TaskManagerService(
        board_repo=board_repo,
        column_repo=column_repo,
        task_repo=task_repo,
        tag_repo=tag_repo,
        history_repo=history_repo
    )

    # 3. Создаём доску
    board = service.create_board(BoardCreate(
        name="Sprint 2024-01",
        description="Планирование спринта"
    ))
    print(f"✅ Создана доска: {board.name} (id={board.id})")

    # 4. Создаём колонки
    columns = [
        service.create_column(board.id, ColumnCreate(name="To Do", position=0)),
        service.create_column(board.id, ColumnCreate(name="In Progress", position=1)),
        service.create_column(board.id, ColumnCreate(name="Review", position=2)),
        service.create_column(board.id, ColumnCreate(name="Done", position=3)),
    ]
    for col in columns:
        print(f"  📌 Колонка: {col.name} (pos={col.position})")

    # 5. Создаём теги
    tags = [
        service.create_tag(TagCreate(name="Bug", color="#FF0000")),
        service.create_tag(TagCreate(name="Feature", color="#00AA00")),
        service.create_tag(TagCreate(name="Documentation", color="#0000FF")),
    ]
    for tag in tags:
        print(f"  🏷️ Тег: {tag.name}")

    # 6. Создаём задачи
    task1 = service.create_task(
        board.id,
        columns[0].id,
        TaskCreate(
            title="Исправить ошибку входа",
            description="Пользователь не может войти при пустом пароле",
            priority=3,
            tags=[tags[0].id]
        )
    )
    print(f"✅ Создана задача: {task1.title} (id={task1.id})")

    task2 = service.create_task(
        board.id,
        columns[0].id,
        TaskCreate(
            title="Реализовать поиск по задачам",
            description="Добавить поиск по названию и тегам",
            priority=2,
            tags=[tags[1].id]
        )
    )
    print(f"✅ Создана задача: {task2.title} (id={task2.id})")

    # 7. Перемещаем задачу (TODO -> IN_PROGRESS)
    moved = service.move_task(task1.id, columns[1].id)
    print(f"↗️ Задача '{moved.title}' перемещена в {moved.status.value}")

    # 8. Обновляем задачу
    updated = service.update_task(
        task2.id,
        TaskCreate(
            title="Реализовать расширенный поиск",
            due_date=datetime.now() + timedelta(days=7)
        )
    )
    print(f"✏️ Задача обновлена: {updated.title}")

    # 9. Получаем статистику
    stats = service.get_board_stats(board.id)
    print(f"\n📊 Статистика доски '{stats['board_name']}':")
    print(f"  Всего задач: {stats['total_tasks']}")
    print(f"  По статусам: {stats['by_status']}")
    print(f"  Просрочено: {stats['overdue_tasks']}")

    # 10. Получаем историю задачи
    history = service.get_task_history(task1.id)
    print(f"\n📜 История задачи '{task1.title}':")
    for h in history:
        print(f"  {h.changed_at}: {h.field_name} -> {h.new_value}")

    # 11. Список задач на доске
    all_tasks = service.list_tasks(board_id=board.id)
    print(f"\n📋 Все задачи на доске:")
    for t in all_tasks:
        print(f"  - [{t.status.value}] {t.title} (приоритет: {t.priority.name})")


if __name__ == "__main__":
    main()