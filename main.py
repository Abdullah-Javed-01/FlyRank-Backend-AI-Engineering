from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Message":"Welcome to first FastAPI application!"}