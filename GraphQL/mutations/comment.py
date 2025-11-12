"""Comment mutations"""

import strawberry
from strawberry.types import Info
from typing import Optional

from shared.services import CommentService
from shared.schemas import CommentCreate as CommentCreateSchema, CommentUpdate as CommentUpdateSchema
from gql_types.comment import Comment, CommentCreateInput, CommentUpdateInput


@strawberry.type
class CommentMutations:
    @strawberry.mutation
    def create_comment(self, info: Info, input: CommentCreateInput) -> Comment:
        """
        Create a new comment.

        GraphQL Characteristic:
        - Nested data creation in single request
        - Returns comment with user info
        """
        if not info.context.user:
            raise Exception("Authentication required")

        comment_data = CommentCreateSchema(
            content=input.content,
            task_id=input.task_id
        )

        db_comment = CommentService.create_comment(
            info.context.db,
            comment_data,
            info.context.user.id
        )

        return Comment(
            id=db_comment.id,
            content=db_comment.content,
            task_id=db_comment.task_id,
            user_id=db_comment.user_id,
            created_at=db_comment.created_at,
            updated_at=db_comment.updated_at
        )

    @strawberry.mutation
    def update_comment(self, info: Info, id: int, input: CommentUpdateInput) -> Optional[Comment]:
        """Update an existing comment"""
        if not info.context.user:
            raise Exception("Authentication required")

        update_data = {}
        if input.content is not None:
            update_data["content"] = input.content

        comment_update = CommentUpdateSchema(**update_data)

        db_comment = CommentService.update_comment(
            info.context.db,
            id,
            comment_update,
            info.context.user.id
        )

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

    @strawberry.mutation
    def delete_comment(self, info: Info, id: int) -> bool:
        """Delete a comment"""
        if not info.context.user:
            raise Exception("Authentication required")

        return CommentService.delete_comment(info.context.db, id, info.context.user.id)
