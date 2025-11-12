"""
WebSocket API - Task Management System

Features WebSocket characteristics:
- Persistent bidirectional connections
- Real-time message broadcasting
- Server-initiated push notifications
- Stateful connection management
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from shared.database import SessionLocal
from shared.auth import decode_access_token
from shared.models import User
from connection_manager import manager
from message_handler import MessageHandler


# Create FastAPI app
app = FastAPI(
    title="Task Management WebSocket API",
    description="WebSocket API for real-time task management",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time communication.

    WebSocket Characteristic:
    - Long-lived connection (not request-response)
    - Bidirectional: client and server can both send messages
    - Authentication via query parameter (since WebSocket doesn't support headers easily)

    Connection Flow:
    1. Client connects with JWT token: ws://localhost:8002/ws?token=<jwt>
    2. Server authenticates token
    3. Connection accepted and tracked
    4. Client sends JSON messages with action types
    5. Server processes and responds
    6. Server can also push unsolicited updates

    Message Format (Client -> Server):
    {
        "action": "task.create",
        "data": { "title": "...", "description": "...", "project_id": 1 }
    }

    Message Format (Server -> Client):
    {
        "type": "task.created",
        "data": { "id": 1, "title": "...", ... }
    }
    """
    # Create database session
    db = SessionLocal()

    try:
        # Authenticate user from token
        payload = decode_access_token(token)
        if not payload:
            await websocket.close(code=4001, reason="Invalid token")
            return

        user_id_str = payload.get("sub")
        if not user_id_str:
            await websocket.close(code=4001, reason="Invalid token payload")
            return

        user_id = int(user_id_str)

        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=4001, reason="User not found")
            return

        # Accept connection and add to manager
        await manager.connect(websocket, user_id)

        # Send welcome message
        import json
        await websocket.send_text(json.dumps({
            "type": "connected",
            "data": {
                "user_id": user_id,
                "username": user.username,
                "active_users": manager.get_active_users(),
                "total_connections": manager.get_connection_count()
            }
        }))

        # Message loop - wait for client messages
        while True:
            # Wait for message from client
            message = await websocket.receive_text()

            # Process message
            await MessageHandler.handle_message(
                websocket,
                message,
                db,
                user_id
            )

    except WebSocketDisconnect:
        # Client disconnected
        manager.disconnect(websocket, user_id)

        # Notify other users
        import json
        await manager.broadcast(json.dumps({
            "type": "user.disconnected",
            "data": {
                "user_id": user_id,
                "active_users": manager.get_active_users()
            }
        }))

    except Exception as e:
        # Error occurred
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)

    finally:
        # Cleanup
        db.close()


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.

    WebSocket Characteristic:
    - Regular HTTP endpoint for info
    - Actual API communication happens over WebSocket (/ws)
    """
    return {
        "message": "Task Management WebSocket API",
        "version": "1.0.0",
        "websocket_endpoint": "/ws",
        "documentation": "Connect to WebSocket with token: ws://localhost:8002/ws?token=<jwt>",
        "active_connections": manager.get_connection_count(),
        "active_users": len(manager.get_active_users())
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_connections": manager.get_connection_count()
    }