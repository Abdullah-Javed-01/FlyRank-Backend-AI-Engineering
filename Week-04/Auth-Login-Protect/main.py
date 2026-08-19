import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, Request, Response
from supabase import Client, create_client
from pydantic import BaseModel
from fastapi.responses import JSONResponse


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class AuthError(Exception):
    def __init__(self, message: str):
        self.message = message

app = FastAPI(title="FlyRank Auth API")

class AuthCredentials(BaseModel):
    email: str | None = None
    password: str | None = None

@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=401,
        content={"error": exc.message},
    )
    
@app.get("/")
def root():
    return {
        "message": "FlyRank Auth API",
        "supabase": "client initialized"
    }
    
def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization:
        raise AuthError("Access token required")

    parts = authorization.split(" ", 1)

    if (
        len(parts) != 2
        or parts[0].lower() != "bearer"
        or not parts[1].strip()
    ):
        raise AuthError("Access token required")

    token = parts[1].strip()

    try:
        response = supabase.auth.get_user(token)

        if not response.user:
            raise AuthError("Invalid or expired token")

        return response.user

    except AuthError:
        raise

    except Exception:
        raise AuthError("Invalid or expired token")
    
@app.get("/protected/profile")
def protected_profile(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "created_at": (
            current_user.created_at.isoformat()
            if hasattr(current_user.created_at, "isoformat")
            else str(current_user.created_at)
        ),
    }
    
@app.get("/protected/dashboard")
def protected_dashboard(current_user=Depends(get_current_user)):
    return {
        "message": "Welcome to your protected dashboard",
        "user_id": str(current_user.id),
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
    
@app.post("/auth/logout", status_code=204)
def logout(current_user=Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return Response(status_code=204)

    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Logout failed"},
        )