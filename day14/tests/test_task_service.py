import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.entities import Board, Column, Task, Tag, TaskStatus, Priority
from domain.exceptions import (
    BoardNotFoundError, ColumnNotFoundError, TaskNotFoundError,
    TagNotFoundError, BusinessRuleViolation, InvalidTaskStatusTransition,
    ValidationError
)
from services.task_service import TaskManagerService
from services.schemas import BoardCreate, ColumnCreate, TaskCreate, TaskUpdate, TagCreate


class TestTaskManagerService:
    """Тесты для TaskManagerService"""

    @pytest.fixture
    def mock_repos(self):
        """Создаём моки всех репозиториев"""
        return {
            'board': Mock(),
            'column': Mock(),
            'task': Mock(),
            'tag': Mock(),
            'history': Mock()
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Создаём сервис с моками"""
        return TaskManagerService(
            board_repo=mock_repos['board'],
            column_repo=mock_repos['column'],
            task_repo=mock_repos['task'],
            tag_repo=mock_repos['tag'],
            history_repo=mock_repos['history']
        )

    # ==================== Тесты для досок ====================

    def test_create_board_success(self, service, mock_repos):
        """Тест: успешное создание доски"""
        board_data = BoardCreate(name="Test Board", description="Test Description")
        expected_board = Board(id=1, name="Test Board", description="Test Description")
        mock_repos['board'].save.return_value = expected_board

        result = service.create_board(board_data)

        assert result.id == 1
        assert result.name == "Test Board"
        mock_repos['board'].save.assert_called_once()

    def test_get_board_success(self, service, mock_repos):
        """Тест: успешное получение доски"""
        expected_board = Board(id=1, name="Test Board")
        mock_repos['board'].find_by_id.return_value = expected_board

        result = service.get_board(1)

        assert result.id == 1
        assert result.name == "Test Board"
        mock_repos['board'].find_by_id.assert_called_once_with(1)

    def test_get_board_not_found(self, service, mock_repos):
        """Тест: попытка получить несуществующую доску"""
        mock_repos['board'].find_by_id.return_value = None

        with pytest.raises(BoardNotFoundError, match="Доска с id=999 не найдена"):
            service.get_board(999)

    def test_list_boards_success(self, service, mock_repos):
        """Тест: успешное получение списка досок"""
        boards = [
            Board(id=1, name="Board 1"),
            Board(id=2, name="Board 2")
        ]
        mock_repos['board'].find_all.return_value = boards

        result = service.list_boards()

        assert len(result) == 2
        assert result[0].name == "Board 1"
        mock_repos['board'].find_all.assert_called_once_with(100, 0)

    def test_delete_board_success(self, service, mock_repos):
        """Тест: успешное удаление доски"""
        board = Board(id=1, name="Test Board")
        mock_repos['board'].find_by_id.return_value = board
        mock_repos['task'].find_by_board.return_value = []
        mock_repos['column'].find_by_board.return_value = []
        mock_repos['board'].delete.return_value = True

        result = service.delete_board(1)

        assert result is True
        mock_repos['board'].delete.assert_called_once_with(1)

    # ==================== Тесты для колонок ====================

    def test_create_column_success(self, service, mock_repos):
        """Тест: успешное создание колонки"""
        mock_repos['board'].find_by_id.return_value = Board(id=1, name="Board")
        mock_repos['column'].find_by_board.return_value = []
        expected_column = Column(id=1, board_id=1, name="To Do", position=0)
        mock_repos['column'].save.return_value = expected_column

        result = service.create_column(1, ColumnCreate(name="To Do", position=0))

        assert result.id == 1
        assert result.name == "To Do"
        mock_repos['column'].save.assert_called_once()

    def test_create_column_duplicate_position(self, service, mock_repos):
        """Тест: попытка создать колонку с занятой позицией"""
        mock_repos['board'].find_by_id.return_value = Board(id=1, name="Board")
        existing_column = Column(id=1, board_id=1, name="Existing", position=0)
        mock_repos['column'].find_by_board.return_value = [existing_column]

        with pytest.raises(BusinessRuleViolation, match="Позиция 0 уже занята"):
            service.create_column(1, ColumnCreate(name="New", position=0))

    def test_list_columns_success(self, service, mock_repos):
        """Тест: успешное получение списка колонок"""
        mock_repos['board'].find_by_id.return_value = Board(id=1, name="Board")
        columns = [
            Column(id=1, board_id=1, name="To Do", position=0),
            Column(id=2, board_id=1, name="Done", position=1)
        ]
        mock_repos['column'].find_by_board.return_value = columns

        result = service.list_columns(1)

        assert len(result) == 2
        assert result[0].position == 0

    # ==================== Тесты для задач ====================

    def test_create_task_success(self, service, mock_repos):
        """Тест: успешное создание задачи"""
        mock_repos['board'].find_by_id.return_value = Board(id=1, name="Board")
        mock_repos['column'].find_by_id.return_value = Column(id=1, board_id=1, name="To Do", position=0)
        mock_repos['tag'].find_by_id.return_value = Tag(id=1, name="Bug")
        expected_task = Task(
            id=1, board_id=1, column_id=1, title="Fix bug",
            priority=Priority.HIGH, tags=[1]
        )
        mock_repos['task'].save.return_value = expected_task

        task_data = TaskCreate(title="Fix bug", priority=Priority.HIGH, tags=[1])
        result = service.create_task(1, 1, task_data)

        assert result.id == 1
        assert result.title == "Fix bug"
        mock_repos['task'].save.assert_called_once()

    def test_create_task_invalid_column(self, service, mock_repos):
        """Тест: попытка создать задачу в колонке другой доски"""
        mock_repos['board'].find_by_id.return_value = Board(id=1, name="Board")
        mock_repos['column'].find_by_id.return_value = Column(id=1, board_id=2, name="Wrong", position=0)

        task_data = TaskCreate(title="Task")

        with pytest.raises(ValidationError, match="Колонка не принадлежит указанной доске"):
            service.create_task(1, 1, task_data)

    def test_get_task_success(self, service, mock_repos):
        """Тест: успешное получение задачи"""
        expected_task = Task(id=1, board_id=1, column_id=1, title="Task")
        mock_repos['task'].find_by_id.return_value = expected_task

        result = service.get_task(1)

        assert result.id == 1
        assert result.title == "Task"

    def test_get_task_not_found(self, service, mock_repos):
        """Тест: попытка получить несуществующую задачу"""
        mock_repos['task'].find_by_id.return_value = None

        with pytest.raises(TaskNotFoundError, match="Задача с id=999 не найдена"):
            service.get_task(999)

    def test_move_task_success(self, service, mock_repos):
        """Тест: успешное перемещение задачи"""
        task = Task(id=1, board_id=1, column_id=1, title="Task", status=TaskStatus.TODO)
        mock_repos['task'].find_by_id.return_value = task

        new_column = Column(id=2, board_id=1, name="In Progress", position=1)
        mock_repos['column'].find_by_id.return_value = new_column

        columns = [
            Column(id=1, board_id=1, name="To Do", position=0),
            Column(id=2, board_id=1, name="In Progress", position=1)
        ]
        mock_repos['column'].find_by_board.return_value = columns

        updated_task = Task(id=1, board_id=1, column_id=2, title="Task", status=TaskStatus.IN_PROGRESS)
        mock_repos['task'].save.return_value = updated_task

        result = service.move_task(1, 2)

        assert result.column_id == 2
        assert result.status == TaskStatus.IN_PROGRESS

    def test_move_task_invalid_transition(self, service, mock_repos):
        """Тест: недопустимый переход статуса"""
        task = Task(id=1, board_id=1, column_id=2, title="Task", status=TaskStatus.IN_PROGRESS)
        mock_repos['task'].find_by_id.return_value = task

        new_column = Column(id=1, board_id=1, name="To Do", position=0)
        mock_repos['column'].find_by_id.return_value = new_column

        columns = [
            Column(id=1, board_id=1, name="To Do", position=0),
            Column(id=2, board_id=1, name="In Progress", position=1)
        ]
        mock_repos['column'].find_by_board.return_value = columns

        with pytest.raises(InvalidTaskStatusTransition):
            service.move_task(1, 1)

    def test_delete_task_success(self, service, mock_repos):
        """Тест: успешное удаление задачи"""
        task = Task(id=1, board_id=1, column_id=1, title="Task")
        mock_repos['task'].find_by_id.return_value = task
        mock_repos['task'].delete.return_value = True

        result = service.delete_task(1)

        assert result is True
        mock_repos['task'].delete.assert_called_once_with(1)

    # ==================== Тесты для тегов ====================

    def test_create_tag_success(self, service, mock_repos):
        """Тест: успешное создание тега"""
        mock_repos['tag'].find_all.return_value = []
        expected_tag = Tag(id=1, name="Bug", color="#FF0000")
        mock_repos['tag'].save.return_value = expected_tag

        tag_data = TagCreate(name="Bug", color="#FF0000")
        result = service.create_tag(tag_data)

        assert result.id == 1
        assert result.name == "Bug"
        mock_repos['tag'].save.assert_called_once()

    def test_create_tag_duplicate(self, service, mock_repos):
        """Тест: попытка создать дубликат тега"""
        existing_tag = Tag(id=1, name="Bug", color="#FF0000")
        mock_repos['tag'].find_all.return_value = [existing_tag]

        tag_data = TagCreate(name="Bug", color="#00FF00")

        with pytest.raises(BusinessRuleViolation, match="Тег с именем 'Bug' уже существует"):
            service.create_tag(tag_data)

    def test_list_tags_success(self, service, mock_repos):
        """Тест: успешное получение списка тегов"""
        tags = [
            Tag(id=1, name="Bug", color="#FF0000"),
            Tag(id=2, name="Feature", color="#00FF00")
        ]
        mock_repos['tag'].find_all.return_value = tags

        result = service.list_tags()

        assert len(result) == 2
        assert result[0].name == "Bug"

    # ==================== Тесты для статистики ====================

    def test_get_board_stats_success(self, service, mock_repos):
        """Тест: успешное получение статистики доски"""
        mock_repos['board'].find_by_id.return_value = Board(id=1, name="Board")
        tasks = [
            Task(id=1, board_id=1, column_id=1, title="Task1", status=TaskStatus.TODO, priority=Priority.HIGH),
            Task(id=2, board_id=1, column_id=1, title="Task2", status=TaskStatus.IN_PROGRESS, priority=Priority.MEDIUM),
            Task(id=3, board_id=1, column_id=1, title="Task3", status=TaskStatus.DONE, priority=Priority.LOW),
        ]
        mock_repos['task'].find_by_board.return_value = tasks

        stats = service.get_board_stats(1)

        assert stats["total_tasks"] == 3
        assert stats["by_status"]["todo"] == 1
        assert stats["by_status"]["in_progress"] == 1
        assert stats["by_status"]["done"] == 1

    def test_get_board_stats_with_overdue(self, service, mock_repos):
        """Тест: статистика с просроченными задачами"""
        mock_repos['board'].find_by_id.return_value = Board(id=1, name="Board")
        tasks = [
            Task(
                id=1, board_id=1, column_id=1, title="Task1",
                status=TaskStatus.TODO, priority=Priority.HIGH,
                due_date=datetime.now() - timedelta(days=1)
            ),
            Task(
                id=2, board_id=1, column_id=1, title="Task2",
                status=TaskStatus.DONE, priority=Priority.MEDIUM,
                due_date=datetime.now() - timedelta(days=2)
            ),
        ]
        mock_repos['task'].find_by_board.return_value = tasks

        stats = service.get_board_stats(1)

        assert stats["total_tasks"] == 2
        assert stats["overdue_tasks"] == 1