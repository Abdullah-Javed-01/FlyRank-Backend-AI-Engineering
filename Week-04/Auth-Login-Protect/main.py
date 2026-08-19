import os

from dotenv import load_dotenv
from fastapi import FastAPI, Header
from supabase import Client, create_client
from pydantic import BaseModel
from fastapi.responses import JSONResponse


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="FlyRank Auth API")

class AuthCredentials(BaseModel):
    email: str | None = None
    password: str | None = None

@app.get("/")
def root():
    return {
        "message": "FlyRank Auth API",
        "supabase": "client initialized"
    }
    
@app.post("/auth/signup")
def signup(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    try:
        response = supabase.auth.sign_up(
            {
                "email": credentials.email,
                "password": credentials.password,
            }
        )

        return JSONResponse(
            status_code=201,
            content={
                "user": response.user.model_dump(mode="json")
                if response.user
                else None
            }
        )

    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content={"error": str(exc)}
        )
        
@app.post("/auth/login")
def login(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": credentials.email,
                "password": credentials.password,
            }
        )

        if not response.session:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid login credentials"}
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )
        
@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }
    
@app.get("/protected/profile")
def protected_profile(authorization: str | None = Header(default=None)):
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"},
        )

    parts = authorization.split(" ", 1)

    if (
        len(parts) != 2
        or parts[0].lower() != "bearer"
        or not parts[1].strip()
    ):
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"},
        )

    token = parts[1].strip()

    return {
        "message": "Token received",
        "protected": True,
    }