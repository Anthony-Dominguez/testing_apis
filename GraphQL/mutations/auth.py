"""Authentication mutations"""

import strawberry
from strawberry.types import Info

from shared.services import UserService
from shared.schemas import UserCreate as UserCreateSchema
from gql_types.user import User, UserCreateInput, LoginInput
from gql_types.common import Token


@strawberry.type
class AuthMutations:
    @strawberry.mutation
    def register(self, info: Info, input: UserCreateInput) -> User:
        """
        Register a new user.

        GraphQL Characteristic:
        - Single mutation endpoint
        - Returns user object (client selects fields)
        """
        user_data = UserCreateSchema(
            username=input.username,
            email=input.email,
            password=input.password,
            full_name=input.full_name
        )

        db_user = UserService.create_user(info.context.db, user_data)

        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            created_at=db_user.created_at
        )

    @strawberry.mutation
    def login(self, info: Info, input: LoginInput) -> Token:
        """
        Login and get JWT token.

        GraphQL Characteristic:
        - Returns token type
        - Client can request specific fields
        """
        token = UserService.authenticate_user(
            info.context.db,
            input.username,
            input.password
        )

        if not token:
            raise Exception("Invalid username or password")

        return Token(access_token=token)
