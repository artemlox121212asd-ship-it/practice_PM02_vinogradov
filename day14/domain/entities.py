from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Board:
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Column:
    id: int
    board_id: int
    name: str
    position: int  # Порядок отображения
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Tag:
    id: int
    name: str
    color: str = "#808080"  # HEX цвет


@dataclass
class Task:
    id: int
    board_id: int
    column_id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    assignee_id: Optional[int] = None  # ID пользователя (упрощённо)
    due_date: Optional[datetime] = None
    tags: List[int] = field(default_factory=list)  # Список ID тегов
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskHistory:
    id: int
    task_id: int
    changed_by: int
    field_name: str
    old_value: str
    new_value: str
    changed_at: datetime = field(default_factory=datetime.now)