"""
Project service - handles project-related business logic.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status

from ..models import Project
from ..schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project operations"""

    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate, owner_id: int) -> Project:
        """Create a new project owned by the current user"""
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            owner_id=owner_id
        )

        db.add(db_project)
        db.commit()
        db.refresh(db_project)

        return db_project

    @staticmethod
    def get_project(db: Session, project_id: int, user_id: int) -> Optional[Project]:
        """
        Get project by ID.

        Authorization: Only owner can access the project.
        """
        project = db.query(Project).filter(Project.id == project_id).first()

        if project and project.owner_id == user_id:
            return project

        return None

    @staticmethod
    def get_user_projects(db: Session, user_id: int) -> List[Project]:
        """Get all projects owned by a user"""
        return db.query(Project).filter(Project.owner_id == user_id).all()

    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        project_update: ProjectUpdate,
        user_id: int
    ) -> Optional[Project]:
        """
        Update project.

        Authorization: Only owner can update.
        """
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            return None

        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this project"
            )

        # Update fields
        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def delete_project(db: Session, project_id: int, user_id: int) -> bool:
        """
        Delete project.

        Authorization: Only owner can delete.
        Cascades to tasks and comments.
        """
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            return False

        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this project"
            )

        db.delete(project)
        db.commit()

        return True
