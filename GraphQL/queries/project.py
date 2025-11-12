"""Project queries"""

import strawberry
from strawberry.types import Info
from typing import List, Optional

from shared.services import ProjectService
from gql_types.project import Project


@strawberry.type
class ProjectQueries:
    @strawberry.field
    def projects(self, info: Info) -> List[Project]:
        """
        Get all projects for the current user.

        GraphQL Characteristic:
        - Single query can fetch projects with tasks, comments
        - Client controls response shape
        """
        if not info.context.user:
            raise Exception("Authentication required")

        db_projects = ProjectService.get_user_projects(info.context.db, info.context.user.id)

        return [
            Project(
                id=p.id,
                name=p.name,
                description=p.description,
                owner_id=p.owner_id,
                created_at=p.created_at,
                updated_at=p.updated_at
            )
            for p in db_projects
        ]

    @strawberry.field
    def project(self, info: Info, id: int) -> Optional[Project]:
        """Get a single project by ID"""
        if not info.context.user:
            raise Exception("Authentication required")

        db_project = ProjectService.get_project(info.context.db, id, info.context.user.id)

        if not db_project:
            return None

        return Project(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            owner_id=db_project.owner_id,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )
