# SQLite Task CRUD API

A database-backed REST API built with **Python**, **FastAPI**, and **SQLite** for managing tasks.

This project was completed as part of the **FlyRank Backend AI Engineering Internship — Week 3, Assignment A2: Connecting Your CRUD to the Database**.

It continues the Week 2 CRUD API by replacing the temporary in-memory Python list with a persistent SQLite database while keeping the same CRUD endpoints and overall request/response behavior.

---

## What Changed from Week 2?

In Week 2, tasks were stored in a Python list:

```text
Client -> FastAPI -> In-memory Python list
```

Restarting the server caused newly created or updated data to disappear.

In Week 3, the storage layer was replaced with SQLite:

```text
Client -> FastAPI -> SQLite database (tasks.db)
```

The API endpoints remain the same, but task data now survives application restarts.

---

## Features

- Create new tasks
- List all tasks
- Retrieve a task by ID
- Update task title and/or completion status
- Delete tasks
- Persistent SQLite storage
- Automatic database creation
- Automatic `tasks` table creation
- Three example tasks seeded only when the table is empty
- Parameterized SQL queries
- Input validation
- JSON error responses
- Correct HTTP status codes
- Swagger UI documentation
- Database inspection using DB Browser for SQLite

---

## Tech Stack

- Python 3.12
- FastAPI
- Uvicorn
- SQLite
- Python `sqlite3`
- DB Browser for SQLite
- Git
- GitHub

---

## Why SQLite?

SQLite was chosen because it is lightweight, requires no separate database server, and stores the database in a single file.

Python includes the `sqlite3` module in its standard library, so no additional database package is required.

Unlike the Week 2 in-memory list, SQLite provides persistence, meaning created and updated tasks remain available after the FastAPI server stops and starts again.

---

## Database

The application uses:

```text
tasks.db
```

The database is created automatically inside the Week 3 project directory when the application starts.

The database file itself is excluded from Git using `.gitignore`, so each cloned copy of the project creates its own fresh database automatically.

The application also creates the `tasks` table automatically if it does not already exist.

### Tasks Table

| Column | Type | Purpose |
|---|---|---|
| `id` | INTEGER | Primary key |
| `title` | TEXT | Task title |
| `done` | BOOLEAN | Completion status stored by SQLite as `0` or `1` |

If the table is empty when the application starts, three example tasks are inserted automatically.

---

## Project Structure

```text
CRUD-Database/
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
    └── database-browser.png
```

Generated SQLite files such as `tasks.db`, `tasks.db-journal`, `tasks.db-wal`, and `tasks.db-shm` are ignored by Git.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Abdullah-Javed-01/FlyRank-Backend-AI-Engineering.git
cd FlyRank-Backend-AI-Engineering
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r Week-03/CRUD-Database/requirements.txt
```

---

## Running the API

Move into the Week 3 project:

```bash
cd Week-03/CRUD-Database
```

Start the development server:

```bash
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

On the first run, `tasks.db` and the `tasks` table are created automatically.

---

## API Endpoints

| Method | Endpoint | Description | Success Status |
|---|---|---|---|
| `GET` | `/` | API information | `200 OK` |
| `GET` | `/health` | Health check | `200 OK` |
| `GET` | `/tasks` | Return all tasks | `200 OK` |
| `GET` | `/tasks/{task_id}` | Return one task | `200 OK` |
| `POST` | `/tasks` | Create a task | `201 Created` |
| `PUT` | `/tasks/{task_id}` | Update a task | `200 OK` |
| `DELETE` | `/tasks/{task_id}` | Delete a task | `204 No Content` |

Invalid request bodies return:

```text
400 Bad Request
```

Unknown task IDs return:

```text
404 Not Found
```

---

## SQL Queries

All CRUD operations use SQL queries with parameterized placeholders instead of inserting user input directly into SQL strings.

Example:

```sql
SELECT id, title, done FROM tasks WHERE id = ?;
```

The task ID is supplied separately to the query.

Parameterized queries help prevent SQL injection and keep database access safer.

---

## SQL Explored Manually

The database was opened using **DB Browser for SQLite** and the following queries were executed manually:

```sql
SELECT * FROM tasks;
```

```sql
SELECT * FROM tasks WHERE done = 1;
```

```sql
SELECT COUNT(*) FROM tasks;
```

```sql
UPDATE tasks SET done = 1;
```

```sql
DELETE FROM tasks WHERE done = 1;
```

### Example SQL Query

```sql
SELECT * FROM tasks WHERE done = 1;
```

This query returned only tasks marked as completed, where SQLite stores the `done` value as `1`.

Changes made directly in DB Browser were visible through the FastAPI endpoints after the database transaction was committed, because both the API and DB Browser use the same SQLite database file.

---

## Database Screenshot

The screenshot below shows the `tasks` table opened in DB Browser for SQLite.

![SQLite database in DB Browser](screenshots/database-browser.png)

The screenshot includes tasks created through the API, demonstrating that the data was stored persistently in SQLite.

---

## Persistence Test

Persistence was tested by:

1. Creating new tasks through `POST /tasks`
2. Confirming them through `GET /tasks`
3. Stopping the FastAPI server
4. Restarting the server
5. Calling `GET /tasks` again

The created tasks remained available after the restart.

Database changes made manually through DB Browser were also verified through the API.

---

## Automatic Database Setup

A clean copy of the project requires no manual database setup.

When the application starts:

1. SQLite creates `tasks.db` if it does not exist.
2. The application creates the `tasks` table if it does not exist.
3. The application counts the existing rows.
4. If the table is empty, three example tasks are inserted.
5. If tasks already exist, no duplicate seed data is added.

This allows someone cloning the repository to start the API without manually creating the database.

---

## Storage Layer Separation

The external API remains the same while the storage implementation changes.

```text
Week 2:
API -> Python list

Week 3:
API -> SQLite
```

This demonstrates an important backend engineering idea: the API describes what the application does, while the database is an implementation detail describing where the data is stored.

---

## What I Learned

Through this assignment I practiced:

- SQLite database fundamentals
- Persistent data storage
- SQL `SELECT`
- SQL `INSERT`
- SQL `UPDATE`
- SQL `DELETE`
- SQL `WHERE`
- SQL `COUNT`
- Primary keys
- Database tables, rows, and columns
- Parameterized SQL queries
- SQLite transactions
- Python's `sqlite3` module
- Inspecting databases with DB Browser for SQLite
- Separating the API layer from the storage layer
- Testing persistence across server restarts
- Incremental Git commits

---

## Development Stages

The database migration was implemented incrementally:

```text
Stage 0: create SQLite database
Stage 1: database read endpoints
Stage 2: insert into database
Stage 3: update and delete with SQL
Stage 4: explored SQLite
Stage 5: database documentation
```

---

## Author

**Abdullah Javed**

Backend AI Engineering Intern — FlyRank AI

- GitHub: [Abdullah-Javed-01](https://github.com/Abdullah-Javed-01)
- LinkedIn: [Abdullah Javed](https://www.linkedin.com/in/abdullah-javed-id01/)
