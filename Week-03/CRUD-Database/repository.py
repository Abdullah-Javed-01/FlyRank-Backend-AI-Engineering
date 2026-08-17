import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def initialize_database():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )

            cursor.execute("SELECT COUNT(*) FROM tasks")
            task_count = cursor.fetchone()[0]

            if task_count == 0:
                example_tasks = [
                    ("Task 1", False),
                    ("Task 2", True),
                    ("Task 3", False),
                ]

                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    example_tasks,
                )


def row_to_task(row):
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }


def get_tasks():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            )
            rows = cursor.fetchall()

    return [row_to_task(row) for row in rows]


def get_task(task_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s",
                (task_id,),
            )
            row = cursor.fetchone()

    if row is None:
        return None

    return row_to_task(row)


def create_task(title):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                RETURNING id, title, done
                """,
                (title, False),
            )
            row = cursor.fetchone()

    return row_to_task(row)


def update_task(task_id, title=None, done=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s",
                (task_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            updated_title = title if title is not None else row[1]
            updated_done = done if done is not None else bool(row[2])

            cursor.execute(
                """
                UPDATE tasks
                SET title = %s, done = %s
                WHERE id = %s
                RETURNING id, title, done
                """,
                (updated_title, updated_done, task_id),
            )

            updated_row = cursor.fetchone()

    return row_to_task(updated_row)


def delete_task(task_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id",
                (task_id,),
            )

            return cursor.fetchone() is not None