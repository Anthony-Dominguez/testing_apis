"""Comment GraphQL types"""

import strawberry
from datetime import datetime


@strawberry.type
class Comment:
    id: int
    text: str
    task_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime


@strawberry.input
class CommentCreateInput:
    text: str
    task_id: int


@strawberry.input
class CommentUpdateInput:
    text: str