"""Shared utility helpers used across routers."""
from datetime import datetime, timezone
from fastapi import Response, HTTPException

from db import db


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean(doc: dict) -> dict:
    if not doc:
        return doc
    doc.pop("_id", None)
    return doc


def clean_list(docs: list) -> list:
    return [clean(d) for d in docs]


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )


# Time helpers used by booking slot computation
def to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def from_minutes(mins: int) -> str:
    return f"{mins // 60:02d}:{mins % 60:02d}"


async def require_practitioner_profile(user: dict) -> dict:
    """Lookup helper — raises 404 if the logged-in user has no practitioner profile."""
    prac = await db.practitioners.find_one({"user_id": user["id"]})
    if not prac:
        raise HTTPException(status_code=404, detail="Practitioner profile not found")
    return prac


async def enrich_practitioner(prac: dict) -> dict:
    """Hydrate a practitioner doc with services, portfolio, reviews, availability, badges, verifications."""
    pid = prac["id"]
    services = await db.services.find({"practitioner_id": pid, "is_active": True}).sort("display_order", 1).to_list(200)
    portfolio = await db.portfolio_items.find({"practitioner_id": pid}).sort("display_order", 1).to_list(200)
    reviews = await db.reviews.find({"practitioner_id": pid, "is_visible": True}).sort("created_at", -1).to_list(100)
    availability = await db.availability.find({"practitioner_id": pid}).to_list(20)
    badges = await db.practitioner_badges.find({"practitioner_id": pid, "is_active": True}).to_list(20)
    verifications = await db.practitioner_verifications.find({"practitioner_id": pid}).to_list(20)
    prac["services"] = clean_list(services)
    prac["portfolio"] = clean_list(portfolio)
    prac["reviews"] = clean_list(reviews)
    prac["availability"] = clean_list(availability)
    prac["badges"] = [b["badge_type"] for b in badges]
    prac["verifications"] = [{"type": v["verification_type"], "status": v["status"]} for v in verifications]
    return prac
