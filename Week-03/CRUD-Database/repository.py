import sqlite3
from pathlib import Path


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


def row_to_task(row):
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }


def get_tasks():
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            "SELECT id, title, done FROM tasks"
        ).fetchall()

    return [row_to_task(row) for row in rows]


def get_task(task_id):
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        return None

    return row_to_task(row)


def create_task(title):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, False),
        )

        new_task_id = cursor.lastrowid

        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (new_task_id,),
        ).fetchone()

    return row_to_task(row)


def update_task(task_id, title=None, done=None):
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if row is None:
            return None

        updated_title = title if title is not None else row[1]
        updated_done = done if done is not None else bool(row[2])

        connection.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (updated_title, updated_done, task_id),
        )

        updated_row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return row_to_task(updated_row)


def delete_task(task_id):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        return cursor.rowcount > 0