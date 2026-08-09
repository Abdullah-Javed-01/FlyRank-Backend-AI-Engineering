from fastapi import FastAPI
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

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        content={"error": "Task " + str(task_id) + " not found"},
        status_code=404
)

@app.post("/tasks", status_code=201)
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

@app.get("/")
def get_values():
    return {
            "name": "Task API",
            "version": "1.0",
            "endpoints": ["/tasks"]
            }

@app.get("/health")
def get_health():
    return {"status": "ok"}