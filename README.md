# API Learning Project

A hands-on project to learn and compare different API paradigms by building the same Task Management system three different ways: REST, GraphQL, and WebSockets.

## Why This Project?

I wanted to truly understand the differences between REST, GraphQL, and WebSocket APIs - not just read about them, but actually build the same features using each approach and see the trade-offs firsthand.

## What's Inside

This project implements a simple task management system with:
- User authentication
- Projects and tasks
- Comments on tasks
- Full CRUD operations

The interesting part? I'm implementing the exact same features three times using different API styles so I can directly compare how each one handles the same problems.

## Current Status

✅ **REST API** - Complete
- Traditional RESTful endpoints
- Multiple URLs for different resources
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Query parameters for filtering
- Interactive documentation at `/docs`

🚧 **GraphQL API** - Coming soon
- Single endpoint with flexible queries
- Client controls what data to fetch
- Nested data in one request

🚧 **WebSocket API** - Coming soon
- Real-time bidirectional communication
- Event-driven architecture
- Live updates without polling

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Auth**: JWT tokens with bcrypt
- **Package Manager**: uv

## Quick Start

1. Install dependencies:
```bash
uv sync
```

2. Initialize the database:
```bash
uv run python init_db.py
```

3. Start the REST API:
```bash
cd REST
uv run uvicorn main:app --reload --port 8000
```

4. Check out the interactive docs:
```
http://localhost:8000/docs
```

## Demo Credentials

- Username: `alice` | Password: `password123`
- Username: `bob` | Password: `password123`

## Project Structure

```
apis/
├── shared/           # Business logic shared by all three APIs
│   ├── models.py    # Database models
│   ├── schemas.py   # Data validation
│   ├── auth.py      # Authentication
│   └── services/    # Business logic
├── REST/            # REST API implementation
├── GraphQL/         # GraphQL API (coming soon)
└── websokets/       # WebSocket API (coming soon)
```

## What I'm Learning

- How each API paradigm handles the same CRUD operations
- When to use REST vs GraphQL vs WebSockets
- The trade-offs between simplicity and flexibility
- Real-world authentication patterns
- How different APIs handle real-time updates

## Next Steps

- [ ] Implement GraphQL API
- [ ] Implement WebSocket API
- [ ] Add automated test scripts
- [ ] Write comparison guide
- [ ] Add example client applications

## License

MIT - Feel free to use this for your own learning!