"""Project GraphQL types"""

import strawberry
from typing import Optional
from datetime import datetime


@strawberry.type
class Project:
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime


@strawberry.input
class ProjectCreateInput:
    name: str
    description: Optional[str] = None


@strawberry.input
class ProjectUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None