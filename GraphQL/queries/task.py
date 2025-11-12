"""Task queries"""

import strawberry
from strawberry.types import Info
from typing import List, Optional

from shared.services import TaskService
from shared.models import TaskStatus as DBTaskStatus
from gql_types.task import Task
from gql_types.common import TaskStatus


def convert_status_from_db(status: DBTaskStatus) -> TaskStatus:
    """Convert DB TaskStatus to GraphQL TaskStatus"""
    status_map = {
        DBTaskStatus.TODO: TaskStatus.TODO,
        DBTaskStatus.IN_PROGRESS: TaskStatus.IN_PROGRESS,
        DBTaskStatus.DONE: TaskStatus.DONE
    }
    return status_map[status]


@strawberry.type
class TaskQueries:
    @strawberry.field
    def tasks(
        self,
        info: Info,
        project_id: Optional[int] = None,
        status: Optional[TaskStatus] = None
    ) -> List[Task]:
        """
        Get tasks with optional filtering.

        GraphQL Characteristic:
        - Single endpoint with flexible parameters
        - Client specifies exact fields needed
        - Can request nested data (project, assignee, comments)
        """
        if not info.context.user:
            raise Exception("Authentication required")

        db_status = None
        if status:
            status_map = {
                TaskStatus.TODO: DBTaskStatus.TODO,
                TaskStatus.IN_PROGRESS: DBTaskStatus.IN_PROGRESS,
                TaskStatus.DONE: DBTaskStatus.DONE
            }
            db_status = status_map[status]

        db_tasks = TaskService.get_tasks(
            info.context.db,
            info.context.user.id,
            project_id,
            db_status
        )

        return [
            Task(
                id=t.id,
                title=t.title,
                description=t.description,
                status=convert_status_from_db(t.status),
                project_id=t.project_id,
                assignee_id=t.assignee_id,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in db_tasks
        ]

    @strawberry.field
    def task(self, info: Info, id: int) -> Optional[Task]:
        """Get a single task by ID"""
        if not info.context.user:
            raise Exception("Authentication required")

        db_task = TaskService.get_task(info.context.db, id, info.context.user.id)

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
