"""Reviews router."""
import uuid
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from db import db
from schemas import ReviewIn
from utils import clean, utcnow_iso

router = APIRouter(tags=["reviews"])


@router.post("/reviews")
async def post_review(body: ReviewIn, user: dict = Depends(get_current_user)):
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Only clients can review")
    b = await db.bookings.find_one({"id": body.booking_id, "client_id": user["id"]})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    if b["status"] != "completed":
        raise HTTPException(status_code=400, detail="Can only review completed bookings")
    existing = await db.reviews.find_one({"booking_id": body.booking_id})
    if existing:
        raise HTTPException(status_code=409, detail="Already reviewed")
    doc = {
        "id": str(uuid.uuid4()),
        "booking_id": body.booking_id,
        "client_id": user["id"],
        "client_name": user["name"],
        "practitioner_id": b["practitioner_id"],
        "rating": body.rating,
        "text": body.text,
        "client_photo_urls": body.client_photo_urls,
        "is_visible": True,
        "created_at": utcnow_iso(),
    }
    await db.reviews.insert_one(doc)
    revs = await db.reviews.find({"practitioner_id": b["practitioner_id"], "is_visible": True}).to_list(500)
    avg = sum(r["rating"] for r in revs) / len(revs)
    await db.practitioners.update_one(
        {"id": b["practitioner_id"]},
        {"$set": {"avg_rating": round(avg, 2), "total_reviews": len(revs)}},
    )
    return clean(doc)
