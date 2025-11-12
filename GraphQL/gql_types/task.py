"""Task GraphQL types"""

import strawberry
from typing import Optional
from datetime import datetime
from .common import TaskStatus


@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    project_id: int
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: datetime


@strawberry.input
class TaskCreateInput:
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    project_id: int
    assignee_id: Optional[int] = None


@strawberry.input
class TaskUpdateInput:
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None