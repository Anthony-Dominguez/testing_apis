"""
Task service - handles task-related business logic.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status

from ..models import Task, Project, TaskStatus
from ..schemas import TaskCreate, TaskUpdate


class TaskService:
    """Service for task operations"""

    @staticmethod
    def _user_can_access_task(db: Session, task: Task, user_id: int) -> bool:
        """Check if user can access task (must own the project)"""
        project = db.query(Project).filter(Project.id == task.project_id).first()
        return project and project.owner_id == user_id

    @staticmethod
    def create_task(db: Session, task_data: TaskCreate, user_id: int) -> Task:
        """
        Create a new task.

        Business rules:
        - User must own the project
        - Status defaults to TODO if not provided
        """
        # Verify user owns the project
        project = db.query(Project).filter(Project.id == task_data.project_id).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create tasks in this project"
            )

        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            project_id=task_data.project_id,
            assignee_id=task_data.assignee_id
        )

        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        return db_task

    @staticmethod
    def get_task(db: Session, task_id: int, user_id: int) -> Optional[Task]:
        """Get task by ID with authorization check"""
        task = db.query(Task).filter(Task.id == task_id).first()

        if task and TaskService._user_can_access_task(db, task, user_id):
            return task

        return None

    @staticmethod
    def get_tasks(
        db: Session,
        user_id: int,
        project_id: Optional[int] = None,
        status: Optional[TaskStatus] = None
    ) -> List[Task]:
        """
        Get tasks with optional filters.

        Only returns tasks from projects owned by the user.
        """
        # Get user's project IDs
        user_project_ids = [p.id for p in db.query(Project).filter(Project.owner_id == user_id).all()]

        # Build query
        query = db.query(Task).filter(Task.project_id.in_(user_project_ids))

        # Apply filters
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)

        return query.all()

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        task_update: TaskUpdate,
        user_id: int
    ) -> Optional[Task]:
        """Update task with authorization check"""
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            return None

        if not TaskService._user_can_access_task(db, task, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this task"
            )

        # Update fields
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int) -> bool:
        """Delete task with authorization check"""
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            return False

        if not TaskService._user_can_access_task(db, task, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this task"
            )

        db.delete(task)
        db.commit()

        return True
