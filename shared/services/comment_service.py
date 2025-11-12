"""
Comment service - handles comment-related business logic.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status

from ..models import Comment, Task, Project
from ..schemas import CommentCreate, CommentUpdate


class CommentService:
    """Service for comment operations"""

    @staticmethod
    def _user_can_access_comment(db: Session, comment: Comment, user_id: int) -> bool:
        """Check if user can access comment (must own the project)"""
        task = db.query(Task).filter(Task.id == comment.task_id).first()
        if not task:
            return False

        project = db.query(Project).filter(Project.id == task.project_id).first()
        return project and project.owner_id == user_id

    @staticmethod
    def create_comment(db: Session, comment_data: CommentCreate, author_id: int) -> Comment:
        """
        Create a new comment.

        Business rules:
        - User must own the project containing the task
        - Author is set to current user
        """
        # Verify task exists and user has access
        task = db.query(Task).filter(Task.id == comment_data.task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        project = db.query(Project).filter(Project.id == task.project_id).first()
        if not project or project.owner_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to comment on this task"
            )

        db_comment = Comment(
            text=comment_data.text,
            task_id=comment_data.task_id,
            author_id=author_id
        )

        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return db_comment

    @staticmethod
    def get_comment(db: Session, comment_id: int, user_id: int) -> Optional[Comment]:
        """Get comment by ID with authorization check"""
        comment = db.query(Comment).filter(Comment.id == comment_id).first()

        if comment and CommentService._user_can_access_comment(db, comment, user_id):
            return comment

        return None

    @staticmethod
    def get_task_comments(db: Session, task_id: int, user_id: int) -> List[Comment]:
        """Get all comments for a task"""
        # Verify user has access to the task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return []

        project = db.query(Project).filter(Project.id == task.project_id).first()
        if not project or project.owner_id != user_id:
            return []

        return db.query(Comment).filter(Comment.task_id == task_id).all()

    @staticmethod
    def update_comment(
        db: Session,
        comment_id: int,
        comment_update: CommentUpdate,
        user_id: int
    ) -> Optional[Comment]:
        """
        Update comment.

        Business rules:
        - Only the author can update their comment
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()

        if not comment:
            return None

        if comment.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this comment"
            )

        comment.text = comment_update.text

        db.commit()
        db.refresh(comment)

        return comment

    @staticmethod
    def delete_comment(db: Session, comment_id: int, user_id: int) -> bool:
        """
        Delete comment.

        Business rules:
        - Only the author can delete their comment
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()

        if not comment:
            return False

        if comment.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this comment"
            )

        db.delete(comment)
        db.commit()

        return True
