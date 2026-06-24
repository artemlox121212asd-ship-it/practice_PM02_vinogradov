from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities import Board, Column, Task, Tag, TaskHistory


class BoardRepository(ABC):
    @abstractmethod
    def save(self, board: Board) -> Board:
        pass

    @abstractmethod
    def find_by_id(self, board_id: int) -> Optional[Board]:
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Board]:
        pass

    @abstractmethod
    def delete(self, board_id: int) -> bool:
        pass


class ColumnRepository(ABC):
    @abstractmethod
    def save(self, column: Column) -> Column:
        pass

    @abstractmethod
    def find_by_id(self, column_id: int) -> Optional[Column]:
        pass

    @abstractmethod
    def find_by_board(self, board_id: int) -> List[Column]:
        pass

    @abstractmethod
    def delete(self, column_id: int) -> bool:
        pass

    @abstractmethod
    def update_position(self, column_id: int, new_position: int) -> bool:
        pass


class TaskRepository(ABC):
    @abstractmethod
    def save(self, task: Task) -> Task:
        pass

    @abstractmethod
    def find_by_id(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def find_by_board(self, board_id: int) -> List[Task]:
        pass

    @abstractmethod
    def find_by_column(self, column_id: int) -> List[Task]:
        pass

    @abstractmethod
    def find_by_assignee(self, assignee_id: int) -> List[Task]:
        pass

    @abstractmethod
    def find_by_tags(self, tag_ids: List[int]) -> List[Task]:
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        pass

    @abstractmethod
    def update_status(self, task_id: int, new_status: str) -> bool:
        pass


class TagRepository(ABC):
    @abstractmethod
    def save(self, tag: Tag) -> Tag:
        pass

    @abstractmethod
    def find_by_id(self, tag_id: int) -> Optional[Tag]:
        pass

    @abstractmethod
    def find_all(self) -> List[Tag]:
        pass

    @abstractmethod
    def delete(self, tag_id: int) -> bool:
        pass


class HistoryRepository(ABC):
    @abstractmethod
    def save(self, history: TaskHistory) -> TaskHistory:
        pass

    @abstractmethod
    def find_by_task(self, task_id: int) -> List[TaskHistory]:
        pass