import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Task CRUD API")

DATABASE_PATH = Path(__file__).with_name("tasks.db")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    done: bool = False

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title cannot be empty")
        return value


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("title cannot be empty")
        return value


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0, 1))
            )
            """
        )

        count = connection.execute(
            "SELECT COUNT(*) AS total FROM tasks"
        ).fetchone()["total"]

        if count == 0:
            connection.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Learn Python", 0),
                    ("Build CRUD API", 0),
                    ("Connect SQLite database", 1),
                ],
            )


def serialize_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


initialize_database()


@app.get("/")
def root():
    return {"message": "Task CRUD API is running"}


@app.get("/tasks")
def list_tasks():
    try:
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            ).fetchall()
        return [serialize_task(row) for row in rows]
    except sqlite3.Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="task_id must be greater than zero",
        )

    try:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
    except sqlite3.Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return serialize_task(row)


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                (task.title, int(task.done)),
            )
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
    except sqlite3.Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return serialize_task(row)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    if task_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="task_id must be greater than zero",
        )

    if task.title is None and task.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide title or done to update",
        )

    try:
        with get_connection() as connection:
            current = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

            if current is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found",
                )

            new_title = task.title if task.title is not None else current["title"]
            new_done = int(task.done) if task.done is not None else current["done"]

            connection.execute(
                "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                (new_title, new_done, task_id),
            )

            updated = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
    except HTTPException:
        raise
    except sqlite3.Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return serialize_task(updated)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    if task_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="task_id must be greater than zero",
        )

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,),
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found",
                )
    except HTTPException:
        raise
    except sqlite3.Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
