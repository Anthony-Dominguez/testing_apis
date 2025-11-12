"""User GraphQL types"""

import strawberry
from typing import Optional
from datetime import datetime


@strawberry.type
class User:
    """User type - client selects exact fields needed"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime


@strawberry.input
class UserCreateInput:
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


@strawberry.input
class UserUpdateInput:
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None


@strawberry.input
class LoginInput:
    username: str
    password: str