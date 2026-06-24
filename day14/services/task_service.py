import logging
from typing import Optional, List
from datetime import datetime

from domain.entities import Board, Column, Task, Tag, TaskHistory, TaskStatus
from domain.exceptions import (
    BoardNotFoundError, ColumnNotFoundError, TaskNotFoundError,
    TagNotFoundError, ValidationError, BusinessRuleViolation,
    InvalidTaskStatusTransition
)
from repositories.interfaces import (
    BoardRepository, ColumnRepository, TaskRepository,
    TagRepository, HistoryRepository
)
from services.schemas import BoardCreate, ColumnCreate, TaskCreate, TaskUpdate, TagCreate

logger = logging.getLogger(__name__)


class TaskManagerService:
    """
    Сервис управления задачами (Trello-like).
    Реализует бизнес-логику: доски, колонки, задачи, теги, история.
    """

    def __init__(
        self,
        board_repo: BoardRepository,
        column_repo: ColumnRepository,
        task_repo: TaskRepository,
        tag_repo: TagRepository,
        history_repo: HistoryRepository
    ):
        self._boards = board_repo
        self._columns = column_repo
        self._tasks = task_repo
        self._tags = tag_repo
        self._history = history_repo
        self._user_id = 1  # Упрощённо: текущий пользователь

    # ==================== Доски ====================

    def create_board(self, data: BoardCreate) -> Board:
        """Создать новую доску"""
        board = Board(
            id=0,
            name=data.name,
            description=data.description
        )
        saved = self._boards.save(board)
        logger.info(f"Доска создана: id={saved.id}, name='{saved.name}'")
        return saved

    def get_board(self, board_id: int) -> Board:
        """Получить доску по ID"""
        board = self._boards.find_by_id(board_id)
        if not board:
            raise BoardNotFoundError(f"Доска с id={board_id} не найдена")
        return board

    def list_boards(self, limit: int = 100, offset: int = 0) -> List[Board]:
        """Получить список досок с пагинацией"""
        return self._boards.find_all(limit, offset)

    def delete_board(self, board_id: int) -> bool:
        """Удалить доску (каскадно удаляем все колонки и задачи)"""
        board = self.get_board(board_id)
        # Удаляем все задачи на доске
        tasks = self._tasks.find_by_board(board_id)
        for task in tasks:
            self._tasks.delete(task.id)
        # Удаляем все колонки
        columns = self._columns.find_by_board(board_id)
        for col in columns:
            self._columns.delete(col.id)
        # Удаляем доску
        result = self._boards.delete(board_id)
        logger.info(f"Доска удалена: id={board_id}")
        return result

    # ==================== Колонки ====================

    def create_column(self, board_id: int, data: ColumnCreate) -> Column:
        """Создать колонку на доске"""
        board = self.get_board(board_id)

        # Проверяем, что позиция не занята
        existing = self._columns.find_by_board(board_id)
        if any(c.position == data.position for c in existing):
            raise BusinessRuleViolation(
                f"Позиция {data.position} уже занята на доске {board_id}"
            )

        column = Column(
            id=0,
            board_id=board_id,
            name=data.name,
            position=data.position
        )
        saved = self._columns.save(column)
        logger.info(f"Колонка создана: id={saved.id}, board={board_id}")
        return saved

    def get_column(self, column_id: int) -> Column:
        """Получить колонку по ID"""
        column = self._columns.find_by_id(column_id)
        if not column:
            raise ColumnNotFoundError(f"Колонка с id={column_id} не найдена")
        return column

    def list_columns(self, board_id: int) -> List[Column]:
        """Получить все колонки доски (сортировка по позиции)"""
        board = self.get_board(board_id)
        columns = self._columns.find_by_board(board_id)
        return sorted(columns, key=lambda c: c.position)

    def move_column(self, column_id: int, new_position: int) -> Column:
        """Переместить колонку на новую позицию"""
        column = self.get_column(column_id)

        if new_position < 0:
            raise ValidationError("Позиция не может быть отрицательной")

        # Проверяем, что новая позиция свободна
        columns = self._columns.find_by_board(column.board_id)
        if any(c.position == new_position and c.id != column_id for c in columns):
            raise BusinessRuleViolation(f"Позиция {new_position} уже занята")

        self._columns.update_position(column_id, new_position)
        column.position = new_position
        logger.info(f"Колонка перемещена: id={column_id}, pos={new_position}")
        return column

    def delete_column(self, column_id: int) -> bool:
        """Удалить колонку (задачи перемещаются в первую колонку)"""
        column = self.get_column(column_id)
        board_id = column.board_id

        # Находим первую колонку доски (минимальная позиция)
        columns = self._columns.find_by_board(board_id)
        if len(columns) <= 1:
            raise BusinessRuleViolation("Нельзя удалить последнюю колонку на доске")

        first_col = min(columns, key=lambda c: c.position)

        # Перемещаем все задачи из удаляемой колонки в первую
        tasks = self._tasks.find_by_column(column_id)
        for task in tasks:
            task.column_id = first_col.id
            self._tasks.save(task)
            logger.debug(f"Задача {task.id} перемещена в колонку {first_col.id}")

        result = self._columns.delete(column_id)
        logger.info(f"Колонка удалена: id={column_id}")
        return result

    # ==================== Задачи ====================

    def create_task(self, board_id: int, column_id: int, data: TaskCreate) -> Task:
        """Создать новую задачу"""
        # Проверяем существование доски и колонки
        board = self.get_board(board_id)
        column = self.get_column(column_id)

        if column.board_id != board_id:
            raise ValidationError("Колонка не принадлежит указанной доске")

        # Проверяем теги
        for tag_id in data.tags:
            if not self._tags.find_by_id(tag_id):
                raise TagNotFoundError(f"Тег с id={tag_id} не найден")

        task = Task(
            id=0,
            board_id=board_id,
            column_id=column_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            assignee_id=data.assignee_id,
            due_date=data.due_date,
            tags=data.tags.copy()
        )
        saved = self._tasks.save(task)

        # Запись в историю
        self._log_history(saved.id, "created", "", f"Задача '{saved.title}' создана")

        logger.info(f"Задача создана: id={saved.id}, title='{saved.title}'")
        return saved

    def get_task(self, task_id: int) -> Task:
        """Получить задачу по ID"""
        task = self._tasks.find_by_id(task_id)
        if not task:
            raise TaskNotFoundError(f"Задача с id={task_id} не найдена")
        return task

    def list_tasks(
        self,
        board_id: Optional[int] = None,
        column_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None
    ) -> List[Task]:
        """Поиск задач с фильтрацией"""
        if board_id:
            self.get_board(board_id)
            return self._tasks.find_by_board(board_id)
        elif column_id:
            self.get_column(column_id)
            return self._tasks.find_by_column(column_id)
        elif assignee_id:
            return self._tasks.find_by_assignee(assignee_id)
        elif tag_ids:
            return self._tasks.find_by_tags(tag_ids)
        else:
            return []

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        """Обновить задачу"""
        task = self.get_task(task_id)

        old_status = task.status

        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.priority is not None:
            task.priority = data.priority
        if data.assignee_id is not None:
            task.assignee_id = data.assignee_id
        if data.due_date is not None:
            task.due_date = data.due_date
        if data.tags is not None:
            # Проверяем теги
            for tag_id in data.tags:
                if not self._tags.find_by_id(tag_id):
                    raise TagNotFoundError(f"Тег с id={tag_id} не найден")
            task.tags = data.tags.copy()

        saved = self._tasks.save(task)
        logger.info(f"Задача обновлена: id={task_id}")
        return saved

    def move_task(self, task_id: int, new_column_id: int) -> Task:
        """Переместить задачу в другую колонку (с проверкой статуса)"""
        task = self.get_task(task_id)
        new_column = self.get_column(new_column_id)

        if task.board_id != new_column.board_id:
            raise ValidationError("Колонка не принадлежит доске задачи")

        old_status = task.status

        # Проверяем допустимость перехода статуса
        # При перемещении в колонку, статус должен соответствовать колонке
        # (упрощённо: предполагаем, что колонки мапятся на статусы по позиции)
        columns = self._columns.find_by_board(task.board_id)
        sorted_cols = sorted(columns, key=lambda c: c.position)

        # Определяем новый статус на основе позиции колонки
        pos_map = {
            0: TaskStatus.TODO,
            1: TaskStatus.IN_PROGRESS,
            2: TaskStatus.REVIEW,
            3: TaskStatus.DONE
        }
        new_status = pos_map.get(new_column.position, TaskStatus.TODO)

        if not self._can_transition(task.status, new_status):
            raise InvalidTaskStatusTransition(
                f"Недопустимый переход статуса: {task.status.value} -> {new_status.value}"
            )

        task.column_id = new_column_id
        task.status = new_status
        saved = self._tasks.save(task)

        self._log_history(
            task_id,
            "status_changed",
            old_status.value,
            new_status.value
        )

        logger.info(f"Задача перемещена: id={task_id}, col={new_column_id}, status={new_status}")
        return saved

    def _can_transition(self, old_status: TaskStatus, new_status: TaskStatus) -> bool:
        """Проверка допустимости перехода статуса"""
        # Разрешённые переходы
        allowed = {
            TaskStatus.TODO: [TaskStatus.IN_PROGRESS, TaskStatus.DONE],
            TaskStatus.IN_PROGRESS: [TaskStatus.REVIEW, TaskStatus.DONE],
            TaskStatus.REVIEW: [TaskStatus.IN_PROGRESS, TaskStatus.DONE],
            TaskStatus.DONE: [TaskStatus.TODO]  # Можно вернуть в работу
        }
        return new_status in allowed.get(old_status, [])

    def delete_task(self, task_id: int) -> bool:
        """Удалить задачу"""
        self.get_task(task_id)
        result = self._tasks.delete(task_id)
        logger.info(f"Задача удалена: id={task_id}")
        return result

    # ==================== Теги ====================

    def create_tag(self, data: TagCreate) -> Tag:
        """Создать новый тег"""
        # Проверяем уникальность имени
        existing = self._tags.find_all()
        if any(t.name.lower() == data.name.lower() for t in existing):
            raise BusinessRuleViolation(f"Тег с именем '{data.name}' уже существует")

        tag = Tag(id=0, name=data.name, color=data.color)
        saved = self._tags.save(tag)
        logger.info(f"Тег создан: id={saved.id}, name='{saved.name}'")
        return saved

    def list_tags(self) -> List[Tag]:
        """Получить все теги"""
        return self._tags.find_all()

    def delete_tag(self, tag_id: int) -> bool:
        """Удалить тег (удалить из всех задач)"""
        tag = self._tags.find_by_id(tag_id)
        if not tag:
            raise TagNotFoundError(f"Тег с id={tag_id} не найден")

        # Удаляем тег из всех задач
        tasks = self._tasks.find_by_tags([tag_id])
        for task in tasks:
            if tag_id in task.tags:
                task.tags.remove(tag_id)
                self._tasks.save(task)

        result = self._tags.delete(tag_id)
        logger.info(f"Тег удалён: id={tag_id}")
        return result

    # ==================== История ====================

    def _log_history(self, task_id: int, field_name: str, old_value: str, new_value: str):
        """Внутренний метод для записи истории"""
        history = TaskHistory(
            id=0,
            task_id=task_id,
            changed_by=self._user_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value
        )
        self._history.save(history)

    def get_task_history(self, task_id: int) -> List[TaskHistory]:
        """Получить историю изменений задачи"""
        self.get_task(task_id)
        return self._history.find_by_task(task_id)

    # ==================== Отчётность ====================

    def get_board_stats(self, board_id: int) -> dict:
        """Получить статистику по доске"""
        board = self.get_board(board_id)
        tasks = self._tasks.find_by_board(board_id)

        stats = {
            "board_id": board_id,
            "board_name": board.name,
            "total_tasks": len(tasks),
            "by_status": {},
            "by_priority": {},
            "overdue_tasks": 0
        }

        for task in tasks:
            # По статусам
            status_key = task.status.value
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

            # По приоритетам
            priority_key = task.priority.name
            stats["by_priority"][priority_key] = stats["by_priority"].get(priority_key, 0) + 1

            # Просроченные
            if task.due_date and task.due_date < datetime.now() and task.status != TaskStatus.DONE:
                stats["overdue_tasks"] += 1

        return stats