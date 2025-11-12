"""
Authentication router for REST API.

Endpoints:
- POST /auth/register - Create new user account
- POST /auth/login - Get JWT access token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.schemas import UserCreate, UserResponse, Token
from shared.services import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    **REST Characteristics:**
    - POST method for creating resources
    - 201 Created status on success
    - Returns created resource

    **Request Body:**
    - username: Unique username (3-50 chars)
    - email: Valid email address
    - password: Minimum 6 characters
    - full_name: Optional full name

    **Response:**
    - User object (without password)
    """
    return UserService.create_user(db, user_data)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login to get JWT access token.

    **REST Characteristics:**
    - Uses OAuth2 password flow (standard)
    - Returns bearer token
    - Token expires in 30 minutes

    **Request Body (form data):**
    - username: User's username
    - password: User's password

    **Response:**
    - access_token: JWT token for authentication
    - token_type: "bearer"

    **Usage:**
    Include token in subsequent requests:
    ```
    Authorization: Bearer <access_token>
    ```
    """
    token = UserService.authenticate_user(db, form_data.username, form_data.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": token, "token_type": "bearer"}
