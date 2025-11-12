"""
Tasks router for REST API.

Endpoints:
- GET /tasks - List tasks with filtering
- POST /tasks - Create new task
- GET /tasks/{task_id} - Get specific task
- PUT /tasks/{task_id} - Update task
- PATCH /tasks/{task_id} - Partially update task
- DELETE /tasks/{task_id} - Delete task
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from shared.database import get_db
from shared.dependencies import get_current_user
from shared.schemas import TaskCreate, TaskUpdate, TaskResponse
from shared.models import User, TaskStatus
from shared.services import TaskService

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List tasks with optional filtering.

    **REST Characteristics:**
    - Query parameters for filtering
    - Returns array of resources
    - Flexible filtering options

    **Query Parameters:**
    - project_id: Filter tasks by project (optional)
    - status: Filter by status (todo, in_progress, done) (optional)

    **Authorization:**
    - Only returns tasks from user's projects

    **Example:**
    - `/tasks` - All user's tasks
    - `/tasks?status=in_progress` - Only in-progress tasks
    - `/tasks?project_id=1&status=todo` - Todo tasks in project 1

    **Requires:** Authentication token
    """
    return TaskService.get_tasks(db, current_user.id, project_id, status)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task.

    **REST Characteristics:**
    - POST method for creation
    - 201 Created status
    - Returns created resource

    **Request Body:**
    - title: Task title (required)
    - description: Optional description
    - status: todo, in_progress, or done (default: todo)
    - project_id: Project to add task to (required)
    - assignee_id: Optional user assignment

    **Authorization:**
    - User must own the project

    **Requires:** Authentication token
    """
    return TaskService.create_task(db, task_data, current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific task by ID.

    **REST Characteristics:**
    - Path parameter for resource ID
    - 404 if not found

    **Authorization:**
    - User must own the project containing the task

    **Requires:** Authentication token
    """
    task = TaskService.get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update task (full update).

    **REST Characteristics:**
    - PUT method for full replacement
    - All fields can be updated
    - Returns updated resource

    **Request Body:**
    - All fields optional
    - Only provided fields are updated

    **Authorization:**
    - User must own the project

    **Requires:** Authentication token
    """
    task = TaskService.update_task(db, task_id, task_update, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def partial_update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Partially update task.

    **REST Characteristics:**
    - PATCH method for partial updates
    - Semantically indicates partial modification
    - Functionally same as PUT in this implementation

    **Common Use Case:**
    Update only task status:
    ```json
    {"status": "done"}
    ```

    **Requires:** Authentication token
    """
    task = TaskService.update_task(db, task_id, task_update, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task.

    **REST Characteristics:**
    - DELETE method for removal
    - 204 No Content (no response body)
    - Cascades to comments

    **Authorization:**
    - User must own the project

    **Requires:** Authentication token
    """
    if not TaskService.delete_task(db, task_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )