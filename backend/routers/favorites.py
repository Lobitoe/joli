"""Favorites router."""
import uuid
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from db import db
from schemas import FavoriteIn
from utils import clean_list, utcnow_iso

router = APIRouter(tags=["favorites"])


@router.get("/me/favorites")
async def list_favorites(user: dict = Depends(get_current_user)):
    if user["role"] != "client":
        return []
    favs = await db.favorites.find({"client_id": user["id"]}).to_list(500)
    pids = [f["practitioner_id"] for f in favs]
    if not pids:
        return []
    pracs = await db.practitioners.find({"id": {"$in": pids}}).to_list(500)
    pracs = clean_list(pracs)
    for p in pracs:
        thumbs = await db.portfolio_items.find({"practitioner_id": p["id"]}).limit(2).to_list(2)
        p["portfolio_thumbs"] = [t["image_url"] for t in thumbs]
    return pracs


@router.post("/me/favorites")
async def add_favorite(body: FavoriteIn, user: dict = Depends(get_current_user)):
    if user["role"] != "client":
        raise HTTPException(status_code=403)
    existing = await db.favorites.find_one({"client_id": user["id"], "practitioner_id": body.practitioner_id})
    if existing:
        return {"ok": True}
    await db.favorites.insert_one({
        "id": str(uuid.uuid4()),
        "client_id": user["id"],
        "practitioner_id": body.practitioner_id,
        "created_at": utcnow_iso(),
    })
    return {"ok": True}


@router.delete("/me/favorites/{practitioner_id}")
async def remove_favorite(practitioner_id: str, user: dict = Depends(get_current_user)):
    await db.favorites.delete_one({"client_id": user["id"], "practitioner_id": practitioner_id})
    return {"ok": True}
