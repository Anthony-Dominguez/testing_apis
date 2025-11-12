"""
WebSocket Connection Manager - Manages active WebSocket connections.

WebSocket Characteristic:
- Maintains persistent connections
- Broadcasts messages to multiple clients
- Tracks connected users
"""

from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.

    This is a key component that differentiates WebSocket from REST/GraphQL:
    - REST: Stateless, no connection tracking
    - GraphQL: Stateless (though subscriptions can use WebSocket)
    - WebSocket: Stateful, maintains active connections
    """

    def __init__(self):
        # Active connections: {user_id: set of websocket connections}
        # One user can have multiple connections (multiple tabs/devices)
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Accept new WebSocket connection and track it.

        WebSocket Characteristic:
        - Connection persists until client disconnects or error occurs
        - Multiple connections per user supported
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Remove connection when client disconnects.

        Cleanup is important to prevent memory leaks.
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Remove user entry if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        """
        Send message to all connections of a specific user.

        WebSocket Characteristic:
        - Server can push messages to client
        - No request needed from client
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)

    async def broadcast(self, message: str, exclude_user: int = None):
        """
        Broadcast message to all connected clients.

        WebSocket Characteristic:
        - Real-time updates to all users
        - Perfect for notifications, live updates

        Args:
            message: JSON message to broadcast
            exclude_user: Optional user_id to exclude from broadcast
        """
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue

            for connection in connections:
                await connection.send_text(message)

    def get_active_users(self) -> list[int]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()
