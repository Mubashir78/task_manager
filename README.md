# Navas Task Manager API

A beginner-friendly REST API built with **FastAPI**, **SQLAlchemy**, and **SQLite**.
Covers full CRUD operations, middleware, CORS, Pydantic validation, and dependency injection.

---

## What This Project Covers

- Full CRUD (Create, Read, Update, Delete) for Users and Tasks
- SQLite database with SQLAlchemy ORM
- Pydantic schemas for request validation and response shaping
- Middleware - request logging with timing
- CORS - cross-origin resource sharing configuration
- Dependency injection with `Depends`
- Auto-generated interactive API docs at `/docs`

---

## Project Structure

```
task_manager/
├── main.py          ← app entry point, middleware, CORS, router registration
├── database.py      ← SQLite connection, session factory, get_db dependency
├── models.py        ← SQLAlchemy table definitions (User, Task)
├── schemas.py       ← Pydantic validation schemas
├── crud.py          ← all database operations
├── tasks.db         ← SQLite database file (auto-created on first run)
└── routers/
    ├── __init__.py  ← empty file (makes routers a Python package)
    ├── tasks.py     ← task endpoints (full CRUD)
    └── users.py     ← user endpoints (full CRUD)
```

---

## Requirements

- Python 3.8 or higher

---

## Installation

**1. Clone or create the project folder**

```bash
mkdir task_manager
cd task_manager
mkdir routers
touch routers/__init__.py
```

**2. Install dependencies**

```bash
pip install fastapi uvicorn sqlalchemy
```

---

## Running the Server

```bash
uvicorn main:app --reload
```

The `--reload` flag restarts the server automatically when you save a file — very useful during development.

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## Interactive API Docs

FastAPI generates interactive documentation automatically. Once the server is running, open:

```
http://127.0.0.1:8000/docs
```

You can test every endpoint directly in the browser - no Postman needed.

![API Docs Overview](middleware_logs.png)

All 10 endpoints are grouped neatly by resource - **Users** and **Tasks** - with colour-coded HTTP methods.

---

## API Endpoints

### Users

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/users/` | Create a new user |
| `GET` | `/users/` | List users with optional `skip` and `limit` query params |
| `GET` | `/users/{id}` | Get one user (includes their tasks) |
| `PUT` | `/users/{id}` | Update a user's name or email |
| `DELETE` | `/users/{id}` | Delete a user |

### Tasks

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/tasks/` | Create a new task |
| `GET` | `/tasks/` | List tasks with optional `skip` and `limit` query params |
| `GET` | `/tasks/{id}` | Get one task by ID |
| `PUT` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

---

## Pagination

Both list endpoints (`GET /tasks/` and `GET /users/`) support `skip` and `limit` as
query parameters:

- `skip` — how many records to skip from the start of the result set (default `0`)
- `limit` — the maximum number of records to return (default `10`)

```
GET /tasks/?skip=0&limit=5   →  first 5 tasks
GET /tasks/?skip=5&limit=5   →  next 5 tasks
GET /tasks/                  →  first 10 tasks (defaults)
```

The same behaviour applies to `GET /users/`.

---

## Testing the API - Step by Step

Follow this order to see everything working together.

**Step 1- Create a user**

```json
POST /users/

{
  "name": "Alice",
  "email": "alice@example.com"
}
```

**Step 2 - Create a task for that user**

```json
POST /tasks/

{
  "title": "Learn FastAPI",
  "description": "Build the task manager project",
  "owner_id": 1
}
```

**Step 3 - Fetch the user and see their tasks nested inside the response**

```
GET /users/
```

Response:

```json
[
  {
    "name": "Alice",
    "email": "alice@example.com",
    "id": 1,
    "tasks": [
      {
        "title": "Learn FastAPI",
        "description": "Build the task manager project",
        "id": 1,
        "completed": false,
        "owner_id": 1
      }
    ]
  }
]
```

![GET /users/ response](get_users_response.png)

Notice how the user's tasks are **nested inside the response automatically** - powered by SQLAlchemy's `relationship()` and Pydantic's nested schemas.

**Step 4 - Mark the task as completed**

```json
PUT /tasks/1

{
  "completed": true
}
```

**Step 5 - Update only the user's name (other fields stay the same)**

```json
PUT /users/1

{
  "name": "Alice Wanjiku"
}
```

**Step 6 - Delete the task**

```
DELETE /tasks/1
```

Response:

```json
{
  "message": "Task deleted successfully"
}
```

---

## Middleware - Seeing Every Request in the Terminal

Every request passes through the logging middleware before reaching an endpoint.
You can watch every call printed live in your terminal as you test:

![Middleware terminal logs](docs_overview.png)

Each line shows:
- The HTTP method and full URL
- The response status code (200 = success)
- How long the request took in seconds

This is great for debugging and understanding the request lifecycle.

---

## How the Layers Connect

```
HTTP Request
     ↓
Middleware (logs method, URL, response time)
     ↓
Router (tasks.py or users.py) - handles the endpoint
     ↓
crud.py - performs the database operation
     ↓
SQLAlchemy + SQLite (tasks.db)
     ↑
Response shaped by Pydantic schema → sent back to client
```

---

## Key Concepts Explained

**SQLAlchemy Models vs Pydantic Schemas**

Models define the database tables. Schemas define what data comes in and goes out through the API. They are separate on purpose - you may want to hide certain database fields from the API response, or accept different fields on create vs update.

**The `get_db` dependency**

Every endpoint that needs the database includes `db: Session = Depends(get_db)`. FastAPI calls `get_db()` automatically, opens a session, passes it to the endpoint, and closes it cleanly when the request is done.

**The `from_attributes = True` config**

This tells Pydantic to read data from SQLAlchemy model objects (not just plain dictionaries). Without it, converting a SQLAlchemy result to a Pydantic response would fail.

**Middleware**

Every request passes through the middleware before reaching an endpoint. The logging middleware in this project prints the HTTP method, URL, response status code, and how long the request took.

**CORS**

CORS controls which frontend origins are allowed to call the API. Without it, a browser-based frontend on a different port or domain will be blocked. In development, you can allow all origins with `allow_origins=["*"]`. In production, list only your real frontend URLs.

---

## CORS Configuration

In `main.py`, update the `origins` list to match your frontend:

```python
origins = [
    "http://localhost:3000",    # React
    "http://localhost:5173",    # Vite
]
```

For development only, you can open it completely:

```python
origins = ["*"]  # never use this in production
```

---

## Extending the Project

Good next steps once you are comfortable with this project:

- Add password hashing to the User model with `passlib`
- Add JWT authentication so only logged-in users can create tasks
- Filter tasks by `owner_id` so users only see their own tasks
- Add a `due_date` field to Task using SQLAlchemy's `DateTime` column
- Switch from SQLite to PostgreSQL by changing the `DATABASE_URL`

---

## License

MIT - free to use, modify, and share.