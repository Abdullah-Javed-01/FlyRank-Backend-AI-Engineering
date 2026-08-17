import sqlite3
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
app = FastAPI()

DATABASE_PATH = Path(__file__).with_name("tasks.db")


def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )

        task_count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        if task_count == 0:
            example_tasks = [
                ("Task 1", False),
                ("Task 2", True),
                ("Task 3", False),
            ]

            connection.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                example_tasks,
            )


initialize_database()

def row_to_task(row):
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }

@app.get("/tasks", description="Return all tasks stored in the SQLite database.")
def get_tasks():
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            "SELECT id, title, done FROM tasks"
        ).fetchall()

    return [row_to_task(row) for row in rows]

@app.get("/tasks/{task_id}", description="Return one task by its ID.")
def get_task(task_id: int):
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        return JSONResponse(
            content={"error": "Task not found"},
            status_code=404,
        )

    return row_to_task(row)

@app.post("/tasks", description="Create a new task with done set to false.", status_code=201)
def create_task(task: dict):
    title = task.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            content={"error": "Title is required"},
            status_code=400,
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title.strip(), False),
        )

        new_task_id = cursor.lastrowid

        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (new_task_id,),
        ).fetchone()

    return row_to_task(row)

@app.put("/tasks/{task_id}", description="Update the title and/or done status of a task.")
def update_task(task_id: int, data: dict):
    if "title" not in data and "done" not in data:
        return JSONResponse(
            content={"error": "Request must include title or done"},
            status_code=400,
        )

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return JSONResponse(
                content={"error": "Title must be a non-empty string"},
                status_code=400,
            )

    if "done" in data:
        if not isinstance(data["done"], bool):
            return JSONResponse(
                content={"error": "Done must be a boolean value"},
                status_code=400,
            )

    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if row is None:
            return JSONResponse(
                content={"error": "Task not found"},
                status_code=404,
            )

        updated_title = (
            data["title"].strip()
            if "title" in data
            else row[1]
        )

        updated_done = (
            data["done"]
            if "done" in data
            else bool(row[2])
        )

        connection.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (updated_title, updated_done, task_id),
        )

        updated_row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return row_to_task(updated_row)
    
@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task by its ID.")
def delete_task(task_id: int):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        if cursor.rowcount == 0:
            return JSONResponse(
                content={"error": "Task not found"},
                status_code=404,
            )

    return Response(status_code=204)

@app.get("/", description="Return basic information about the Task API.")
def get_values():
    return {
            "name": "Task API",
            "version": "1.0",
            "endpoints": ["/tasks"]
            }

@app.get("/health", description="Check whether the API is running.")
def get_health():
    return {"status": "ok"}