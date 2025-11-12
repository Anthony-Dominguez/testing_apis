"""User mutations"""

import strawberry
from strawberry.types import Info
from typing import Optional

from shared.services import UserService
from shared.schemas import UserUpdate as UserUpdateSchema
from gql_types.user import User, UserUpdateInput


@strawberry.type
class UserMutations:
    @strawberry.mutation
    def update_user(self, info: Info, id: int, input: UserUpdateInput) -> Optional[User]:
        """
        Update an existing user.

        GraphQL Characteristic:
        - Partial updates with optional fields
        - Returns updated user object
        """
        if not info.context.user:
            raise Exception("Authentication required")

        # Only allow users to update themselves
        if info.context.user.id != id:
            raise Exception("Not authorized to update this user")

        update_data = {}
        if input.email is not None:
            update_data["email"] = input.email
        if input.full_name is not None:
            update_data["full_name"] = input.full_name

        user_update = UserUpdateSchema(**update_data)

        db_user = UserService.update_user(info.context.db, id, user_update)

        if not db_user:
            return None

        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            created_at=db_user.created_at
        )

    @strawberry.mutation
    def delete_user(self, info: Info, id: int) -> bool:
        """Delete a user (must be the authenticated user)"""
        if not info.context.user:
            raise Exception("Authentication required")

        # Only allow users to delete themselves
        if info.context.user.id != id:
            raise Exception("Not authorized to delete this user")

        return UserService.delete_user(info.context.db, id)
