"""
GraphQL context - provides database session and current user to resolvers.
"""

from typing import Optional
from strawberry.fastapi import BaseContext
from sqlalchemy.orm import Session
from shared.models import User


class GraphQLContext(BaseContext):
    """Context passed to all GraphQL resolvers"""
    def __init__(self, db: Session, user: Optional[User] = None):
        super().__init__()
        self.db = db
        self.user = user