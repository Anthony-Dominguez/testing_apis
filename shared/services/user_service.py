"""
User service - handles user-related business logic.

Operations:
- User registration
- User authentication
- User CRUD operations
"""

from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status

from ..models import User
from ..schemas import UserCreate, UserUpdate
from ..auth import hash_password, verify_password, create_access_token


class UserService:
    """Service for user operations"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user (registration).

        Business rules:
        - Username must be unique
        - Email must be unique
        - Password is hashed before storage

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            Created user

        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user with hashed password
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password)
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and return JWT token.

        Args:
            db: Database session
            username: Username
            password: Plain text password

        Returns:
            JWT token if authentication successful, None otherwise
        """
        # Find user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None

        # Verify password
        if not verify_password(password, user.hashed_password):
            return None

        # Create and return token
        # JWT standard requires 'sub' to be a string, not an integer
        token_data = {"sub": str(user.id), "username": user.username}
        access_token = create_access_token(token_data)

        return access_token

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """Get list of users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate, current_user_id: int) -> Optional[User]:
        """
        Update user information.

        Business rules:
        - Users can only update their own profile
        - Username and email must remain unique

        Args:
            db: Database session
            user_id: ID of user to update
            user_update: Update data
            current_user_id: ID of user making the request

        Returns:
            Updated user or None if not found/unauthorized

        Raises:
            HTTPException: If not authorized or validation fails
        """
        # Authorization check
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Update fields
        update_data = user_update.model_dump(exclude_unset=True)

        # Check username uniqueness if being updated
        if "username" in update_data and update_data["username"] != user.username:
            existing = db.query(User).filter(User.username == update_data["username"]).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Check email uniqueness if being updated
        if "email" in update_data and update_data["email"] != user.email:
            existing = db.query(User).filter(User.email == update_data["email"]).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )

        # Hash password if being updated
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        # Apply updates
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete_user(db: Session, user_id: int, current_user_id: int) -> bool:
        """
        Delete user account.

        Business rules:
        - Users can only delete their own account

        Args:
            db: Database session
            user_id: ID of user to delete
            current_user_id: ID of user making the request

        Returns:
            True if deleted, False if not found

        Raises:
            HTTPException: If not authorized
        """
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this user"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        db.delete(user)
        db.commit()

        return True
