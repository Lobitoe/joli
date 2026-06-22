"""Auth router: /api/auth/* — register, login, logout, me."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Response

from auth import hash_password, verify_password, create_access_token, get_current_user
from db import db
from schemas import RegisterIn, LoginIn
from utils import set_auth_cookie, utcnow_iso

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(body: RegisterIn, response: Response):
    email = body.email.lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user_id = str(uuid.uuid4())
    doc = {
        "id": user_id,
        "email": email,
        "password_hash": hash_password(body.password),
        "name": body.name,
        "role": body.role,
        "created_at": utcnow_iso(),
    }
    await db.users.insert_one(doc)
    token = create_access_token(user_id, email, body.role)
    set_auth_cookie(response, token)
    return {
        "user": {"id": user_id, "email": email, "name": body.name, "role": body.role},
        "token": token,
    }


@router.post("/login")
async def login(body: LoginIn, response: Response):
    email = body.email.lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user["id"], user["email"], user["role"])
    set_auth_cookie(response, token)
    return {
        "user": {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]},
        "token": token,
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]}
