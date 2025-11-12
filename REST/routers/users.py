"""
Users router for REST API.

Endpoints:
- GET /users - List all users
- GET /users/{user_id} - Get specific user
- PUT /users/{user_id} - Update user
- DELETE /users/{user_id} - Delete user
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from shared.database import get_db
from shared.dependencies import get_current_user
from shared.schemas import UserResponse, UserUpdate
from shared.models import User
from shared.services import UserService

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all users with pagination.

    **REST Characteristics:**
    - GET method for retrieving collections
    - Query parameters for pagination
    - Returns array of resources

    **Query Parameters:**
    - skip: Offset for pagination (default: 0)
    - limit: Max results (default: 100, max: 100)

    **Requires:** Authentication token
    """
    return UserService.get_users(db, skip=skip, limit=limit)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's information.

    **REST Characteristics:**
    - Special endpoint for current user
    - No ID needed (extracted from token)

    **Requires:** Authentication token
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific user by ID.

    **REST Characteristics:**
    - Path parameter for resource ID
    - 404 if not found

    **Requires:** Authentication token
    """
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user information.

    **REST Characteristics:**
    - PUT method for full updates
    - Path parameter for resource ID
    - Returns updated resource

    **Authorization:**
    - Users can only update their own profile

    **Request Body:**
    - All fields optional
    - Only provided fields are updated

    **Requires:** Authentication token
    """
    user = UserService.update_user(db, user_id, user_update, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete user account.

    **REST Characteristics:**
    - DELETE method for resource removal
    - 204 No Content on success (no response body)

    **Authorization:**
    - Users can only delete their own account

    **Requires:** Authentication token
    """
    if not UserService.delete_user(db, user_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )