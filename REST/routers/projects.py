"""
Projects router for REST API.

Endpoints:
- GET /projects - List user's projects
- POST /projects - Create new project
- GET /projects/{project_id} - Get specific project
- PUT /projects/{project_id} - Update project
- DELETE /projects/{project_id} - Delete project
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from shared.database import get_db
from shared.dependencies import get_current_user
from shared.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from shared.models import User
from shared.services import ProjectService

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all projects owned by current user.

    **REST Characteristics:**
    - GET method for collections
    - Automatically filtered by ownership
    - Returns array of resources

    **Requires:** Authentication token
    """
    return ProjectService.get_user_projects(db, current_user.id)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new project.

    **REST Characteristics:**
    - POST method for creation
    - 201 Created status code
    - Returns created resource
    - Location header could be added

    **Request Body:**
    - name: Project name (required)
    - description: Optional description

    **Requires:** Authentication token
    """
    return ProjectService.create_project(db, project_data, current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific project by ID.

    **REST Characteristics:**
    - Path parameter for resource ID
    - 404 if not found or unauthorized

    **Authorization:**
    - Only project owner can view

    **Requires:** Authentication token
    """
    project = ProjectService.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update project information.

    **REST Characteristics:**
    - PUT method for updates
    - Returns updated resource

    **Authorization:**
    - Only project owner can update

    **Request Body:**
    - name: Optional new name
    - description: Optional new description

    **Requires:** Authentication token
    """
    project = ProjectService.update_project(db, project_id, project_update, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project.

    **REST Characteristics:**
    - DELETE method for removal
    - 204 No Content (no response body)
    - Cascades to tasks and comments

    **Authorization:**
    - Only project owner can delete

    **Requires:** Authentication token
    """
    if not ProjectService.delete_project(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )