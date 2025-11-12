"""
GraphQL Schema - combines all queries and mutations.
"""

import strawberry
from queries.user import UserQueries
from queries.project import ProjectQueries
from queries.task import TaskQueries
from queries.comment import CommentQueries
from mutations.auth import AuthMutations
from mutations.user import UserMutations
from mutations.project import ProjectMutations
from mutations.task import TaskMutations
from mutations.comment import CommentMutations


@strawberry.type
class Query(UserQueries, ProjectQueries, TaskQueries, CommentQueries):
    """
    Root Query type.

    GraphQL Characteristic:
    - Single entry point for all queries
    - Client can combine multiple queries in one request
    - All resource types available from one endpoint
    """
    pass


@strawberry.type
class Mutation(AuthMutations, UserMutations, ProjectMutations, TaskMutations, CommentMutations):
    """
    Root Mutation type.

    GraphQL Characteristic:
    - Single entry point for all mutations
    - Can batch multiple mutations in one request
    - All operations available from one endpoint
    """
    pass


# Create the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
