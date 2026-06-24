from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Optional, List
from domain.entities import TaskStatus, Priority


class BoardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Название не может быть пустым')
        return v.strip()


class ColumnCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    position: int = Field(0, ge=0)

    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Название не может быть пустым')
        return v.strip()


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    tags: List[int] = Field(default_factory=list)

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Название задачи не может быть пустым')
        return v.strip()

    @validator('due_date')
    def due_date_not_past(cls, v):
        if v and v < datetime.now():
            raise ValueError('Дата выполнения не может быть в прошлом')
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[Priority] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[int]] = None


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = "#808080"

    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Название тега не может быть пустым')
        return v.strip()

    @validator('color')
    def valid_hex_color(cls, v):
        if not v.startswith('#') or len(v) not in (4, 7):
            raise ValueError('Цвет должен быть в формате HEX')
        return v