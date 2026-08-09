from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()

tasks = [
    {
        "id": 1,
        "title": "Task 1",
        "done": False
    },
    {
        "id": 2,
        "title": "Task 2",
        "done": True
    },
    {
        "id": 3,
        "title": "Task 3",
        "done": False
    }
]

@app.get("/tasks", description="Return all tasks stored in memory.")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", description="Return one task by its ID.")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        content={"error": "Task " + str(task_id) + " not found"},
        status_code=404
)

@app.post("/tasks", description="Create a new task with done set to false.", status_code=201)
def create_task(task: dict):
    if (
            "title" not in task
            or not isinstance(task["title"], str)
            or not task["title"].strip()
        ):
        return JSONResponse(
            content={"error": "Title is required and must be a non-empty string"},
            status_code=400
        )
    next_id = max(task["id"] for task in tasks) + 1 if tasks else 1
    new_task = {
        "id": next_id,
        "title": task["title"].strip(),
        "done": False
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", description="Update the title and/or done status of a task.")
def update_task(task_id: int, data: dict):
    for task in tasks:
        if task["id"] == task_id:
            if "title" not in data and "done" not in data:
                return JSONResponse(
                    content={"error": "Request must include title or done"},
                    status_code=400
                )
            if "title" in data:
                if not isinstance(data["title"], str) or not data["title"].strip():
                    return JSONResponse(
                        content={"error": "Title must be a non-empty string"},
                        status_code=400
                    )
                task["title"] = data["title"].strip()
            if "done" in data:
                if not isinstance(data["done"], bool):
                    return JSONResponse(
                        content={"error": "Done must be a boolean value"},
                        status_code=400
                    )
                task["done"] = data["done"]
            return task
    return JSONResponse(
        content={"error": "Task " + str(task_id) + " not found"},
        status_code=404
    )
    
@app.delete("/tasks/{task_id}", description="Delete a task by its ID.")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return Response(status_code=204)
    return JSONResponse(
        content={"error": "Task " + str(task_id) + " not found"},
        status_code=404
    )

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