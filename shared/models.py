"""
SQLAlchemy ORM models - the single source of truth for data structure.

These models define:
- Database schema
- Relationships between entities
- Default values and constraints

Used by all three APIs (REST, GraphQL, WebSocket).
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class User(Base):
    """
    User model - represents application users.

    Relationships:
    - projects: Projects owned by this user
    - assigned_tasks: Tasks assigned to this user
    - comments: Comments authored by this user
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")


class Project(Base):
    """
    Project model - container for tasks.

    Relationships:
    - owner: User who owns this project
    - tasks: Tasks belonging to this project
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    """
    Task model - individual work items within projects.

    Relationships:
    - project: Project this task belongs to
    - assignee: User assigned to this task (optional)
    - comments: Comments on this task
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")


class Comment(Base):
    """
    Comment model - user comments on tasks.

    Relationships:
    - task: Task this comment belongs to
    - author: User who wrote this comment
    """
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(2000), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")