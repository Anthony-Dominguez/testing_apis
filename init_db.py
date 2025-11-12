#!/usr/bin/env python3
"""
Database initialization script.

This script:
1. Creates all database tables
2. Seeds initial data (demo users, projects, tasks)

Run this ONCE before starting any API:
    uv run python init_db.py
"""

from shared.database import init_db, SessionLocal
from shared.models import User, Project, Task, Comment, TaskStatus
from shared.auth import hash_password

def seed_data():
    """Seed database with demo data"""
    db = SessionLocal()

    try:
        print("Creating demo users...")

        # Create demo users
        user1 = User(
            username="alice",
            email="alice@example.com",
            full_name="Alice Johnson",
            hashed_password=hash_password("password123")
        )
        user2 = User(
            username="bob",
            email="bob@example.com",
            full_name="Bob Smith",
            hashed_password=hash_password("password123")
        )

        db.add(user1)
        db.add(user2)
        db.commit()
        db.refresh(user1)
        db.refresh(user2)

        print(f"✓ Created users: {user1.username}, {user2.username}")

        # Create demo projects
        print("Creating demo projects...")

        project1 = Project(
            name="Website Redesign",
            description="Redesign company website with modern UI/UX",
            owner_id=user1.id
        )
        project2 = Project(
            name="Mobile App",
            description="Develop iOS and Android mobile application",
            owner_id=user1.id
        )
        project3 = Project(
            name="API Development",
            description="Build REST, GraphQL, and WebSocket APIs",
            owner_id=user2.id
        )

        db.add(project1)
        db.add(project2)
        db.add(project3)
        db.commit()
        db.refresh(project1)
        db.refresh(project2)
        db.refresh(project3)

        print(f"✓ Created {3} projects")

        # Create demo tasks
        print("Creating demo tasks...")

        tasks = [
            Task(
                title="Design homepage mockup",
                description="Create high-fidelity mockup for new homepage",
                status=TaskStatus.TODO,
                project_id=project1.id,
                assignee_id=user1.id
            ),
            Task(
                title="Implement navigation menu",
                description="Build responsive navigation menu component",
                status=TaskStatus.IN_PROGRESS,
                project_id=project1.id,
                assignee_id=user1.id
            ),
            Task(
                title="Set up authentication",
                description="Implement user authentication system",
                status=TaskStatus.DONE,
                project_id=project2.id,
                assignee_id=user1.id
            ),
            Task(
                title="Build user profile screen",
                description="Create user profile UI with edit capabilities",
                status=TaskStatus.TODO,
                project_id=project2.id
            ),
            Task(
                title="Implement REST endpoints",
                description="Create all REST API endpoints with proper HTTP methods",
                status=TaskStatus.IN_PROGRESS,
                project_id=project3.id,
                assignee_id=user2.id
            ),
            Task(
                title="Set up GraphQL schema",
                description="Define GraphQL types, queries, and mutations",
                status=TaskStatus.TODO,
                project_id=project3.id,
                assignee_id=user2.id
            ),
        ]

        for task in tasks:
            db.add(task)

        db.commit()
        print(f"✓ Created {len(tasks)} tasks")

        # Create demo comments
        print("Creating demo comments...")

        comments = [
            Comment(
                text="I'll start working on this today",
                task_id=tasks[0].id,
                author_id=user1.id
            ),
            Comment(
                text="Almost done, just need to add mobile responsiveness",
                task_id=tasks[1].id,
                author_id=user1.id
            ),
            Comment(
                text="Completed and tested successfully",
                task_id=tasks[2].id,
                author_id=user1.id
            ),
            Comment(
                text="REST API is going well, on track for completion",
                task_id=tasks[4].id,
                author_id=user2.id
            ),
        ]

        for comment in comments:
            db.add(comment)

        db.commit()
        print(f"✓ Created {len(comments)} comments")

        print("\n" + "="*60)
        print("Database initialized successfully!")
        print("="*60)
        print("\nDemo users:")
        print("  Username: alice | Password: password123")
        print("  Username: bob   | Password: password123")
        print("\nYou can now start any of the three APIs:")
        print("  - REST API:      cd REST && uv run uvicorn main:app --reload --port 8000")
        print("  - GraphQL API:   cd GraphQL && uv run uvicorn main:app --reload --port 8001")
        print("  - WebSocket API: cd websokets && uv run uvicorn main:app --reload --port 8002")
        print("="*60)

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    print("="*60)
    print("  Task Management Database Initialization")
    print("="*60)
    print()

    print("Creating database tables...")
    init_db()
    print("✓ Tables created")
    print()

    seed_data()


if __name__ == "__main__":
    main()