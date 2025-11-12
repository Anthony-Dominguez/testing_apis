"""
Service layer - business logic for all three APIs.

Services encapsulate:
- CRUD operations
- Business rules and validation
- Authorization checks
- Cross-entity operations

All three APIs (REST, GraphQL, WebSocket) call these same services.
"""

from .user_service import UserService
from .project_service import ProjectService
from .task_service import TaskService
from .comment_service import CommentService

__all__ = [
    "UserService",
    "ProjectService",
    "TaskService",
    "CommentService",
]
