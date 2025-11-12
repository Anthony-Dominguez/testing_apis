"""Project mutations"""

import strawberry
from strawberry.types import Info
from typing import Optional

from shared.services import ProjectService
from shared.schemas import ProjectCreate as ProjectCreateSchema, ProjectUpdate as ProjectUpdateSchema
from gql_types.project import Project, ProjectCreateInput, ProjectUpdateInput


@strawberry.type
class ProjectMutations:
    @strawberry.mutation
    def create_project(self, info: Info, input: ProjectCreateInput) -> Project:
        """
        Create a new project.

        GraphQL Characteristic:
        - Single mutation for project creation
        - Returns full project object with selected fields
        """
        if not info.context.user:
            raise Exception("Authentication required")

        project_data = ProjectCreateSchema(
            name=input.name,
            description=input.description
        )

        db_project = ProjectService.create_project(
            info.context.db,
            project_data,
            info.context.user.id
        )

        return Project(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            owner_id=db_project.owner_id,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )

    @strawberry.mutation
    def update_project(self, info: Info, id: int, input: ProjectUpdateInput) -> Optional[Project]:
        """Update an existing project"""
        if not info.context.user:
            raise Exception("Authentication required")

        update_data = {}
        if input.name is not None:
            update_data["name"] = input.name
        if input.description is not None:
            update_data["description"] = input.description

        project_update = ProjectUpdateSchema(**update_data)

        db_project = ProjectService.update_project(
            info.context.db,
            id,
            project_update,
            info.context.user.id
        )

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

    @strawberry.mutation
    def delete_project(self, info: Info, id: int) -> bool:
        """Delete a project"""
        if not info.context.user:
            raise Exception("Authentication required")

        return ProjectService.delete_project(info.context.db, id, info.context.user.id)
