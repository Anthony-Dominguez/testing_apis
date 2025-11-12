"""Task mutations"""

import strawberry
from strawberry.types import Info
from typing import Optional

from shared.services import TaskService
from shared.schemas import TaskCreate as TaskCreateSchema, TaskUpdate as TaskUpdateSchema
from shared.models import TaskStatus as DBTaskStatus
from gql_types.task import Task, TaskCreateInput, TaskUpdateInput
from gql_types.common import TaskStatus


def convert_status_to_db(status: TaskStatus) -> DBTaskStatus:
    """Convert GraphQL TaskStatus to DB TaskStatus"""
    status_map = {
        TaskStatus.TODO: DBTaskStatus.TODO,
        TaskStatus.IN_PROGRESS: DBTaskStatus.IN_PROGRESS,
        TaskStatus.DONE: DBTaskStatus.DONE
    }
    return status_map[status]


def convert_status_from_db(status: DBTaskStatus) -> TaskStatus:
    """Convert DB TaskStatus to GraphQL TaskStatus"""
    status_map = {
        DBTaskStatus.TODO: TaskStatus.TODO,
        DBTaskStatus.IN_PROGRESS: TaskStatus.IN_PROGRESS,
        DBTaskStatus.DONE: TaskStatus.DONE
    }
    return status_map[status]


@strawberry.type
class TaskMutations:
    @strawberry.mutation
    def create_task(self, info: Info, input: TaskCreateInput) -> Task:
        """
        Create a new task.

        GraphQL Characteristic:
        - Input type for structured data
        - Returns created task (client selects fields)
        """
        if not info.context.user:
            raise Exception("Authentication required")

        task_data = TaskCreateSchema(
            title=input.title,
            description=input.description,
            status=convert_status_to_db(input.status),
            project_id=input.project_id,
            assignee_id=input.assignee_id
        )

        db_task = TaskService.create_task(
            info.context.db,
            task_data,
            info.context.user.id
        )

        return Task(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=convert_status_from_db(db_task.status),
            project_id=db_task.project_id,
            assignee_id=db_task.assignee_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )

    @strawberry.mutation
    def update_task(self, info: Info, id: int, input: TaskUpdateInput) -> Optional[Task]:
        """Update an existing task"""
        if not info.context.user:
            raise Exception("Authentication required")

        update_data = {}
        if input.title is not None:
            update_data["title"] = input.title
        if input.description is not None:
            update_data["description"] = input.description
        if input.status is not None:
            update_data["status"] = convert_status_to_db(input.status)
        if input.assignee_id is not None:
            update_data["assignee_id"] = input.assignee_id

        task_update = TaskUpdateSchema(**update_data)

        db_task = TaskService.update_task(
            info.context.db,
            id,
            task_update,
            info.context.user.id
        )

        if not db_task:
            return None

        return Task(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=convert_status_from_db(db_task.status),
            project_id=db_task.project_id,
            assignee_id=db_task.assignee_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )

    @strawberry.mutation
    def delete_task(self, info: Info, id: int) -> bool:
        """Delete a task"""
        if not info.context.user:
            raise Exception("Authentication required")

        return TaskService.delete_task(info.context.db, id, info.context.user.id)
