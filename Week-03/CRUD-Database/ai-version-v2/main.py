import sqlite3
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(title="Task CRUD API - AI Rematch V2")

DATABASE_PATH = Path(__file__).with_name("tasks.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        if count == 0:
            connection.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Task 1", 0),
                    ("Task 2", 1),
                    ("Task 3", 0),
                ],
            )


def task_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


async def read_json_object(request: Request):
    try:
        data = await request.json()
    except Exception:
        return None, JSONResponse(
            status_code=400,
            content={"error": "Invalid request body"},
        )

    if not isinstance(data, dict):
        return None, JSONResponse(
            status_code=400,
            content={"error": "Invalid request body"},
        )

    return data, None


initialize_database()


@app.get("/tasks")
def get_tasks():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        ).fetchall()

    return [task_to_dict(row) for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return task_to_dict(row)


@app.post("/tasks", status_code=201)
async def create_task(request: Request):
    data, error = await read_json_object(request)
    if error:
        return error

    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is not found"},
        )

    # New tasks always start incomplete, even if the client sends done=true.
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title.strip(), 0),
        )

        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return task_to_dict(row)


@app.put("/tasks/{task_id}")
async def update_task(task_id: int, request: Request):
    data, error = await read_json_object(request)
    if error:
        return error

    if "title" not in data and "done" not in data:
        return JSONResponse(
            status_code=400,
            content={"error": "Request must include title or done"},
        )

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title is not found"},
            )

    if "done" in data and not isinstance(data["done"], bool):
        return JSONResponse(
            status_code=400,
            content={"error": "Done must be true or false"},
        )

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if existing is None:
            return JSONResponse(
                status_code=404,
                content={"error": "Task not found"},
            )

        new_title = (
            data["title"].strip()
            if "title" in data
            else existing["title"]
        )
        new_done = (
            int(data["done"])
            if "done" in data
            else existing["done"]
        )

        connection.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, new_done, task_id),
        )

        updated = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return task_to_dict(updated)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        if cursor.rowcount == 0:
            return JSONResponse(
                status_code=404,
                content={"error": "Task not found"},
            )

    return Response(status_code=204)
