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