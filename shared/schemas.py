"""
Pydantic schemas for request/response validation.

These schemas:
- Validate incoming data
- Serialize outgoing data
- Provide API contracts
- Support type hints

Pattern:
- *Base: Shared fields
- *Create: For creating new records (no ID)
- *Update: For updating records (all fields optional)
- *Response: For API responses (includes ID, timestamps, relationships)
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from .models import TaskStatus


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Shared user fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Schema for updating user (all fields optional)"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    """Schema for user in API responses"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Project Schemas
# ============================================================================

class ProjectBase(BaseModel):
    """Shared project fields"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating project (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectResponse(ProjectBase):
    """Schema for project in API responses"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Task Schemas
# ============================================================================

class TaskBase(BaseModel):
    """Shared task fields"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.TODO


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    project_id: int
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    """Schema for updating task (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None


class TaskResponse(TaskBase):
    """Schema for task in API responses"""
    id: int
    project_id: int
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Comment Schemas
# ============================================================================

class CommentBase(BaseModel):
    """Shared comment fields"""
    text: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    """Schema for creating a new comment"""
    task_id: int


class CommentUpdate(BaseModel):
    """Schema for updating comment"""
    text: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(CommentBase):
    """Schema for comment in API responses"""
    id: int
    task_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Authentication Schemas
# ============================================================================

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data encoded in JWT token"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login credentials"""
    username: str
    password: str
