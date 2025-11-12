"""
WebSocket Message Handlers - Process incoming WebSocket messages.

WebSocket Characteristic:
- Message-based communication (not request/response)
- JSON messages with action types
- Handlers process different action types
"""

import json
from typing import Optional
from sqlalchemy.orm import Session

from shared.services import TaskService, ProjectService, CommentService
from shared.schemas import TaskCreate, TaskUpdate, CommentCreate
from connection_manager import manager


class MessageHandler:
    """
    Process WebSocket messages and perform actions.

    Message Format:
    {
        "action": "task.create" | "task.update" | "task.list" | etc.,
        "data": { ... }
    }

    WebSocket Characteristic:
    - Bidirectional: Server responds AND broadcasts to other clients
    - Real-time: Changes instantly visible to all connected users
    """

    @staticmethod
    async def handle_message(
        websocket,
        message: str,
        db: Session,
        user_id: int
    ) -> None:
        """
        Route message to appropriate handler based on action type.

        This is similar to routing in REST, but happens over persistent connection.
        """
        try:
            data = json.loads(message)
            action = data.get("action")
            payload = data.get("data", {})

            if action == "task.list":
                await MessageHandler._handle_task_list(websocket, db, user_id)
            elif action == "task.create":
                await MessageHandler._handle_task_create(websocket, db, user_id, payload)
            elif action == "task.update":
                await MessageHandler._handle_task_update(websocket, db, user_id, payload)
            elif action == "task.delete":
                await MessageHandler._handle_task_delete(websocket, db, user_id, payload)
            elif action == "project.list":
                await MessageHandler._handle_project_list(websocket, db, user_id)
            elif action == "comment.create":
                await MessageHandler._handle_comment_create(websocket, db, user_id, payload)
            elif action == "ping":
                await MessageHandler._handle_ping(websocket)
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Unknown action: {action}"
                }))

        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Invalid JSON"
            }))
        except Exception as e:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))

    @staticmethod
    async def _handle_ping(websocket):
        """Handle ping message (keep-alive)"""
        await websocket.send_text(json.dumps({
            "type": "pong"
        }))

    @staticmethod
    async def _handle_task_list(websocket, db: Session, user_id: int):
        """
        List all tasks for the user.

        WebSocket Characteristic:
        - Client sends request, server responds
        - Similar to REST GET, but over WebSocket
        """
        tasks = TaskService.get_tasks(db, user_id)

        response = {
            "type": "task.list",
            "data": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "project_id": task.project_id,
                    "assignee_id": task.assignee_id,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]
        }

        await websocket.send_text(json.dumps(response))

    @staticmethod
    async def _handle_task_create(websocket, db: Session, user_id: int, payload: dict):
        """
        Create new task.

        WebSocket Characteristic:
        - Creates task
        - Sends confirmation to requester
        - Broadcasts notification to ALL other users (real-time update!)
        """
        task_data = TaskCreate(**payload)
        task = TaskService.create_task(db, task_data, user_id)

        # Send confirmation to requester
        response = {
            "type": "task.created",
            "data": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "project_id": task.project_id,
                "assignee_id": task.assignee_id,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
        }

        await websocket.send_text(json.dumps(response))

        # Broadcast to other users (exclude creator)
        broadcast_message = {
            "type": "task.new",
            "data": {
                "id": task.id,
                "title": task.title,
                "created_by": user_id
            }
        }

        await manager.broadcast(json.dumps(broadcast_message), exclude_user=user_id)

    @staticmethod
    async def _handle_task_update(websocket, db: Session, user_id: int, payload: dict):
        """
        Update existing task.

        WebSocket Characteristic:
        - Updates task
        - Broadcasts change to all users in real-time
        """
        task_id = payload.get("id")
        if not task_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Task ID required"
            }))
            return

        task_data = TaskUpdate(**{k: v for k, v in payload.items() if k != "id"})
        task = TaskService.update_task(db, task_id, task_data, user_id)

        if not task:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Task not found or not authorized"
            }))
            return

        # Send confirmation
        response = {
            "type": "task.updated",
            "data": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "updated_at": task.updated_at.isoformat()
            }
        }

        await websocket.send_text(json.dumps(response))

        # Broadcast update to all other users
        broadcast_message = {
            "type": "task.changed",
            "data": {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "updated_by": user_id
            }
        }

        await manager.broadcast(json.dumps(broadcast_message), exclude_user=user_id)

    @staticmethod
    async def _handle_task_delete(websocket, db: Session, user_id: int, payload: dict):
        """Delete task and broadcast to all users"""
        task_id = payload.get("id")
        if not task_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Task ID required"
            }))
            return

        success = TaskService.delete_task(db, task_id, user_id)

        if not success:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Task not found or not authorized"
            }))
            return

        # Send confirmation
        await websocket.send_text(json.dumps({
            "type": "task.deleted",
            "data": {"id": task_id}
        }))

        # Broadcast deletion
        await manager.broadcast(json.dumps({
            "type": "task.removed",
            "data": {"id": task_id, "deleted_by": user_id}
        }), exclude_user=user_id)

    @staticmethod
    async def _handle_project_list(websocket, db: Session, user_id: int):
        """List all projects for the user"""
        projects = ProjectService.get_user_projects(db, user_id)

        response = {
            "type": "project.list",
            "data": [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "owner_id": project.owner_id,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat()
                }
                for project in projects
            ]
        }

        await websocket.send_text(json.dumps(response))

    @staticmethod
    async def _handle_comment_create(websocket, db: Session, user_id: int, payload: dict):
        """
        Create comment and broadcast to all users.

        Perfect use case for WebSocket:
        - Real-time comment notifications
        - All users see new comments instantly
        """
        comment_data = CommentCreate(**payload)
        comment = CommentService.create_comment(db, comment_data, user_id)

        # Send confirmation
        response = {
            "type": "comment.created",
            "data": {
                "id": comment.id,
                "text": comment.text,
                "task_id": comment.task_id,
                "author_id": comment.author_id,
                "created_at": comment.created_at.isoformat()
            }
        }

        await websocket.send_text(json.dumps(response))

        # Broadcast new comment
        await manager.broadcast(json.dumps({
            "type": "comment.new",
            "data": {
                "id": comment.id,
                "task_id": comment.task_id,
                "author_id": user_id,
                "text": comment.text
            }
        }), exclude_user=user_id)
