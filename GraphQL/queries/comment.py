"""Comment queries"""

import strawberry
from strawberry.types import Info
from typing import List, Optional

from shared.services import CommentService
from gql_types.comment import Comment


@strawberry.type
class CommentQueries:
    @strawberry.field
    def comments(self, info: Info, task_id: int) -> List[Comment]:
        """
        Get all comments for a task.

        GraphQL Characteristic:
        - Nested query structure
        - Can request comment author info
        """
        if not info.context.user:
            raise Exception("Authentication required")

        db_comments = CommentService.get_comments_by_task(info.context.db, task_id)

        return [
            Comment(
                id=c.id,
                content=c.content,
                task_id=c.task_id,
                user_id=c.user_id,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in db_comments
        ]

    @strawberry.field
    def comment(self, info: Info, id: int) -> Optional[Comment]:
        """Get a single comment by ID"""
        if not info.context.user:
            raise Exception("Authentication required")

        db_comment = CommentService.get_comment(info.context.db, id)

        if not db_comment:
            return None

        return Comment(
            id=db_comment.id,
            content=db_comment.content,
            task_id=db_comment.task_id,
            user_id=db_comment.user_id,
            created_at=db_comment.created_at,
            updated_at=db_comment.updated_at
        )
