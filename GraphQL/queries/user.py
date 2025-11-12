"""User queries"""

import strawberry
from strawberry.types import Info
from typing import List, Optional

from shared.services import UserService
from gql_types.user import User


@strawberry.type
class UserQueries:
    @strawberry.field
    def users(self, info: Info) -> List[User]:
        """
        Get all users.

        GraphQL Characteristic:
        - Client can select which user fields to retrieve
        - Single query can get users + nested data
        """
        if not info.context.user:
            raise Exception("Authentication required")

        db_users = UserService.get_users(info.context.db)

        return [
            User(
                id=u.id,
                username=u.username,
                email=u.email,
                full_name=u.full_name,
                created_at=u.created_at
            )
            for u in db_users
        ]

    @strawberry.field
    def user(self, info: Info, id: int) -> Optional[User]:
        """Get a single user by ID"""
        if not info.context.user:
            raise Exception("Authentication required")

        db_user = UserService.get_user(info.context.db, id)

        if not db_user:
            return None

        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            created_at=db_user.created_at
        )

    @strawberry.field
    def me(self, info: Info) -> Optional[User]:
        """
        Get the current authenticated user.

        GraphQL Characteristic:
        - Context provides user from JWT
        - No need to pass user ID
        """
        if not info.context.user:
            raise Exception("Authentication required")

        return User(
            id=info.context.user.id,
            username=info.context.user.username,
            email=info.context.user.email,
            full_name=info.context.user.full_name,
            created_at=info.context.user.created_at
        )
