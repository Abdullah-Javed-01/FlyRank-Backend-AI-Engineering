import os

from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import Client, create_client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="FlyRank Auth API")


@app.get("/")
def root():
    return {
        "message": "FlyRank Auth API",
        "supabase": "client initialized"
    }