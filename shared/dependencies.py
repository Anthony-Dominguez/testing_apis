"""
FastAPI dependencies - reusable across all three APIs.

Dependencies:
- get_current_user: Extract and validate user from JWT token
- Additional dependencies can be added here

Used by REST, GraphQL, and WebSocket APIs.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from .database import get_db
from .auth import decode_access_token
from .models import User

# HTTP Bearer token security scheme
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    How it works:
    1. Extract token from Authorization header
    2. Decode and validate token
    3. Fetch user from database
    4. Return user object

    Usage in routes:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Extract token
    token = credentials.credentials

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user_id from token (JWT sub claim is a string)
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert to integer
    user_id = int(user_id_str)

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication - returns None if no token provided.

    Useful for endpoints that work both with and without authentication.
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload is None:
            return None

        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None

        # Convert string to integer (JWT sub claim is a string)
        user_id = int(user_id_str)

        user = db.query(User).filter(User.id == user_id).first()
        return user
    except:
        return None
