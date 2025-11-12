"""
Comments router for REST API.

Endpoints:
- GET /comments - List comments (by task)
- POST /comments - Create new comment
- GET /comments/{comment_id} - Get specific comment
- PUT /comments/{comment_id} - Update comment
- DELETE /comments/{comment_id} - Delete comment
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from shared.database import get_db
from shared.dependencies import get_current_user
from shared.schemas import CommentCreate, CommentUpdate, CommentResponse
from shared.models import User
from shared.services import CommentService

router = APIRouter()


@router.get("/", response_model=List[CommentResponse])
async def list_comments(
    task_id: Optional[int] = Query(None, description="Filter by task ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List comments with optional filtering.

    **REST Characteristics:**
    - Query parameter for filtering
    - Returns array of resources

    **Query Parameters:**
    - task_id: Get comments for specific task (optional)

    **Authorization:**
    - Only returns comments from user's projects

    **Example:**
    - `/comments?task_id=5` - All comments on task 5

    **Requires:** Authentication token
    """
    if task_id:
        return CommentService.get_task_comments(db, task_id, current_user.id)

    # If no task_id provided, return empty list
    # (In a real app, you might return recent comments or error)
    return []


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment on a task.

    **REST Characteristics:**
    - POST method for creation
    - 201 Created status
    - Returns created resource

    **Request Body:**
    - text: Comment text (required)
    - task_id: Task to comment on (required)

    **Authorization:**
    - User must own the project containing the task
    - Author is automatically set to current user

    **Requires:** Authentication token
    """
    return CommentService.create_comment(db, comment_data, current_user.id)


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific comment by ID.

    **REST Characteristics:**
    - Path parameter for resource ID
    - 404 if not found

    **Authorization:**
    - User must own the project

    **Requires:** Authentication token
    """
    comment = CommentService.get_comment(db, comment_id, current_user.id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update comment text.

    **REST Characteristics:**
    - PUT method for updates
    - Returns updated resource

    **Request Body:**
    - text: New comment text (required)

    **Authorization:**
    - Only comment author can update

    **Requires:** Authentication token
    """
    comment = CommentService.update_comment(db, comment_id, comment_update, current_user.id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment.

    **REST Characteristics:**
    - DELETE method for removal
    - 204 No Content (no response body)

    **Authorization:**
    - Only comment author can delete

    **Requires:** Authentication token
    """
    if not CommentService.delete_comment(db, comment_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )