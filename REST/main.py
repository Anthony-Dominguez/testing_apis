"""
REST API - Task Management System

Features REST characteristics:
- Multiple resource endpoints
- HTTP method semantics (GET, POST, PUT, PATCH, DELETE)
- Query parameters for filtering
- Proper status codes
- Swagger/OpenAPI documentation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, users, projects, tasks, comments

# Create FastAPI app
app = FastAPI(
    title="Task Management REST API",
    description="RESTful API for task management with full CRUD operations",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.

    Returns basic API information and links to documentation.
    """
    return {
        "message": "Task Management REST API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "projects": "/projects",
            "tasks": "/tasks",
            "comments": "/comments",
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}