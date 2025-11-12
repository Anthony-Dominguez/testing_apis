"""Common GraphQL types"""

import strawberry
import enum


@strawberry.enum
class TaskStatus(enum.Enum):
    """Task status enum for GraphQL"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@strawberry.type
class Token:
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"