from typing import Optional, List, Dict
from datetime import datetime
from domain.entities import Board, Column, Task, Tag, TaskHistory, TaskStatus
from repositories.interfaces import (
    BoardRepository, ColumnRepository, TaskRepository,
    TagRepository, HistoryRepository
)
from domain.exceptions import NotFoundError


class InMemoryBoardRepository(BoardRepository):
    def __init__(self):
        self._store: Dict[int, Board] = {}
        self._counter = 1

    def save(self, board: Board) -> Board:
        if board.id is None or board.id == 0:
            board.id = self._counter
            self._counter += 1
        self._store[board.id] = board
        return board

    def find_by_id(self, board_id: int) -> Optional[Board]:
        return self._store.get(board_id)

    def find_all(self, limit: int = 100, offset: int = 0) -> List[Board]:
        boards = list(self._store.values())
        return boards[offset:offset + limit]

    def delete(self, board_id: int) -> bool:
        if board_id in self._store:
            del self._store[board_id]
            return True
        return False


class InMemoryColumnRepository(ColumnRepository):
    def __init__(self):
        self._store: Dict[int, Column] = {}
        self._counter = 1

    def save(self, column: Column) -> Column:
        if column.id is None or column.id == 0:
            column.id = self._counter
            self._counter += 1
        self._store[column.id] = column
        return column

    def find_by_id(self, column_id: int) -> Optional[Column]:
        return self._store.get(column_id)

    def find_by_board(self, board_id: int) -> List[Column]:
        return [col for col in self._store.values() if col.board_id == board_id]

    def delete(self, column_id: int) -> bool:
        if column_id in self._store:
            del self._store[column_id]
            return True
        return False

    def update_position(self, column_id: int, new_position: int) -> bool:
        column = self.find_by_id(column_id)
        if not column:
            return False
        column.position = new_position
        return True


class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self._store: Dict[int, Task] = {}
        self._counter = 1

    def save(self, task: Task) -> Task:
        if task.id is None or task.id == 0:
            task.id = self._counter
            self._counter += 1
        task.updated_at = datetime.now()
        self._store[task.id] = task
        return task

    def find_by_id(self, task_id: int) -> Optional[Task]:
        return self._store.get(task_id)

    def find_by_board(self, board_id: int) -> List[Task]:
        return [t for t in self._store.values() if t.board_id == board_id]

    def find_by_column(self, column_id: int) -> List[Task]:
        return [t for t in self._store.values() if t.column_id == column_id]

    def find_by_assignee(self, assignee_id: int) -> List[Task]:
        return [t for t in self._store.values() if t.assignee_id == assignee_id]

    def find_by_tags(self, tag_ids: List[int]) -> List[Task]:
        result = []
        for task in self._store.values():
            if any(tag_id in task.tags for tag_id in tag_ids):
                result.append(task)
        return result

    def delete(self, task_id: int) -> bool:
        if task_id in self._store:
            del self._store[task_id]
            return True
        return False

    def update_status(self, task_id: int, new_status: str) -> bool:
        task = self.find_by_id(task_id)
        if not task:
            return False
        task.status = TaskStatus(new_status)
        task.updated_at = datetime.now()
        return True


class InMemoryTagRepository(TagRepository):
    def __init__(self):
        self._store: Dict[int, Tag] = {}
        self._counter = 1

    def save(self, tag: Tag) -> Tag:
        if tag.id is None or tag.id == 0:
            tag.id = self._counter
            self._counter += 1
        self._store[tag.id] = tag
        return tag

    def find_by_id(self, tag_id: int) -> Optional[Tag]:
        return self._store.get(tag_id)

    def find_all(self) -> List[Tag]:
        return list(self._store.values())

    def delete(self, tag_id: int) -> bool:
        if tag_id in self._store:
            del self._store[tag_id]
            return True
        return False


class InMemoryHistoryRepository(HistoryRepository):
    def __init__(self):
        self._store: Dict[int, TaskHistory] = {}
        self._counter = 1

    def save(self, history: TaskHistory) -> TaskHistory:
        if history.id is None or history.id == 0:
            history.id = self._counter
            self._counter += 1
        self._store[history.id] = history
        return history

    def find_by_task(self, task_id: int) -> List[TaskHistory]:
        return [h for h in self._store.values() if h.task_id == task_id]