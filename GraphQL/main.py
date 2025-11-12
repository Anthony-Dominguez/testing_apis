"""
GraphQL API - Task Management System

Features GraphQL characteristics:
- Single endpoint for all operations
- Client specifies exact data needed
- Flexible queries and mutations
- GraphiQL playground for testing
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import Session
from typing import Optional

from shared.database import SessionLocal
from shared.auth import decode_access_token
from shared.models import User
from schema import schema
from context import GraphQLContext


# Custom context getter
async def get_context(request: Request):
    """
    Create GraphQL context with database session and current user.

    GraphQL Characteristic:
    - Context is available to all resolvers
    - Handles authentication transparently
    """
    # Create database session
    db = SessionLocal()

    # Extract user from Authorization header
    user = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        payload = decode_access_token(token)
        if payload:
            user_id_str = payload.get("sub")
            if user_id_str:
                # Convert string to integer (JWT sub claim is a string)
                user_id = int(user_id_str)
                user = db.query(User).filter(User.id == user_id).first()

    context = GraphQLContext(db=db, user=user)
    return context


# Create GraphQL router
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)

# Create FastAPI app
app = FastAPI(
    title="Task Management GraphQL API",
    description="GraphQL API for task management with flexible queries",
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

# Include GraphQL router
app.include_router(graphql_app, prefix="/graphql")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.

    GraphQL Characteristic:
    - All operations go through /graphql endpoint
    - GraphiQL playground available for interactive testing
    """
    return {
        "message": "Task Management GraphQL API",
        "version": "1.0.0",
        "graphql_endpoint": "/graphql",
        "playground": "/graphql (open in browser)",
        "documentation": "Use GraphiQL playground to explore schema"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}