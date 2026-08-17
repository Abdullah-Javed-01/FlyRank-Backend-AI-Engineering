from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

import repository


app = FastAPI()

repository.initialize_database()


@app.get("/tasks", description="Return all tasks stored in the SQLite database.")
def get_tasks():
    return repository.get_tasks()


@app.get("/tasks/{task_id}", description="Return one task by its ID.")
def get_task(task_id: int):
    task = repository.get_task(task_id)

    if task is None:
        return JSONResponse(
            content={"error": "Task not found"},
            status_code=404,
        )

    return task


@app.post(
    "/tasks",
    description="Create a new task with done set to false.",
    status_code=201,
)
def create_task(task: dict):
    title = task.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            content={"error": "Title is required"},
            status_code=400,
        )

    return repository.create_task(title.strip())


@app.put(
    "/tasks/{task_id}",
    description="Update the title and/or done status of a task.",
)
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

    title = data["title"].strip() if "title" in data else None
    done = data["done"] if "done" in data else None

    updated_task = repository.update_task(
        task_id,
        title=title,
        done=done,
    )

    if updated_task is None:
        return JSONResponse(
            content={"error": "Task not found"},
            status_code=404,
        )

    return updated_task


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    description="Delete a task by its ID.",
)
def delete_task(task_id: int):
    deleted = repository.delete_task(task_id)

    if not deleted:
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
        "endpoints": ["/tasks"],
    }


@app.get("/health", description="Check whether the API is running.")
def get_health():
    return {"status": "ok"}