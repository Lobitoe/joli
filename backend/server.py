"""Curlnect FastAPI server — Multicultural Beauty Marketplace MVP."""
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import os
import uuid
import logging
from datetime import datetime, timezone, timedelta, date as date_cls, time as time_cls
from typing import List, Optional, Literal

from fastapi import FastAPI, APIRouter, Depends, HTTPException, Response, Request, Query
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_optional_user,
    require_role,
)


# ---------- Mongo ----------
mongo_url = os.environ["MONGO_URL"]
db_name = os.environ["DB_NAME"]
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# ---------- App ----------
app = FastAPI(title="Curlnect API")
api = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("curlnect")


# =====================================================================
# Pydantic models
# =====================================================================
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)
    role: Literal["client", "practitioner"]


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    role: str


class PractitionerUpsertIn(BaseModel):
    display_name: str
    bio: Optional[str] = ""
    profile_photo_url: Optional[str] = None
    practitioner_type: str
    location_type: str
    service_mode: str
    address: Optional[str] = None
    city: str
    province: str
    service_neighbourhoods: List[str] = []
    service_radius_km: Optional[int] = None
    accepted_payments: List[str] = []
    cancellation_policy: Optional[str] = ""
    cancellation_notice_hours: int = 48
    instagram_handle: Optional[str] = None
    whatsapp_number: Optional[str] = None
    languages: List[str] = ["en"]


class ServiceIn(BaseModel):
    category_id: str
    name: str
    description: Optional[str] = None
    price_min: float
    price_max: Optional[float] = None
    duration_minutes_min: int
    duration_minutes_max: Optional[int] = None
    reference_photo_url: Optional[str] = None
    includes_break: bool = False
    break_duration_minutes: Optional[int] = None


class PortfolioItemIn(BaseModel):
    category_id: str
    image_url: str
    caption: Optional[str] = None
    tags: List[str] = []
    is_featured: bool = False


class AvailabilityIn(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool = True


class BookingIn(BaseModel):
    practitioner_id: str
    service_id: str
    booking_date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    service_location: Literal["practitioner_location", "client_location"] = "practitioner_location"
    client_address: Optional[str] = None
    client_notes: Optional[str] = None
    client_source: Literal["marketplace", "direct_link"] = "marketplace"


class ReviewIn(BaseModel):
    booking_id: str
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = None
    client_photo_urls: List[str] = []


# =====================================================================
# Helpers
# =====================================================================
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


# =====================================================================
# Auth endpoints
# =====================================================================
@api.post("/auth/register")
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


@api.post("/auth/login")
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


@api.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}


@api.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]}


# =====================================================================
# Categories
# =====================================================================
@api.get("/categories")
async def list_categories():
    docs = await db.service_categories.find({"is_active": True}).sort("display_order", 1).to_list(500)
    return clean_list(docs)


# =====================================================================
# Practitioners — Discovery
# =====================================================================
@api.get("/practitioners")
async def list_practitioners(
    city: Optional[str] = None,
    category: Optional[str] = None,  # category name OR id
    service_mode: Optional[str] = None,  # clients_come_to_me | i_travel_to_clients | both
    practitioner_type: Optional[str] = None,
):
    q: dict = {}
    if city:
        q["city"] = {"$regex": f"^{city}$", "$options": "i"}
    if practitioner_type:
        q["practitioner_type"] = practitioner_type
    if service_mode:
        if service_mode == "i_travel_to_clients":
            q["service_mode"] = {"$in": ["i_travel_to_clients", "both"]}
        elif service_mode == "clients_come_to_me":
            q["service_mode"] = {"$in": ["clients_come_to_me", "both"]}
        else:
            q["service_mode"] = service_mode

    practitioners = await db.practitioners.find(q).to_list(200)
    practitioners = clean_list(practitioners)

    # Filter by category (by name or id) — find practitioners with at least one service in that category
    if category:
        cat = await db.service_categories.find_one({"$or": [{"id": category}, {"name": {"$regex": f"^{category}$", "$options": "i"}}]})
        if cat:
            cat_id = cat["id"]
            ids_with_cat = await db.services.distinct("practitioner_id", {"category_id": cat_id, "is_active": True})
            practitioners = [p for p in practitioners if p["id"] in ids_with_cat]
        else:
            practitioners = []

    # Attach a few portfolio thumbnails for each
    for p in practitioners:
        thumbs = await db.portfolio_items.find({"practitioner_id": p["id"]}).limit(4).to_list(4)
        p["portfolio_thumbs"] = [t["image_url"] for t in thumbs]
        # Service count and min price
        services = await db.services.find({"practitioner_id": p["id"], "is_active": True}).to_list(100)
        p["service_count"] = len(services)
        p["starting_price"] = min([s["price_min"] for s in services], default=None)
    return practitioners


@api.get("/practitioners/{practitioner_id}")
async def get_practitioner(practitioner_id: str):
    prac = await db.practitioners.find_one({"id": practitioner_id})
    if not prac:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return await _enrich_practitioner(clean(prac))


@api.get("/practitioners/slug/{slug}")
async def get_practitioner_by_slug(slug: str):
    prac = await db.practitioners.find_one({"direct_booking_slug": slug})
    if not prac:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return await _enrich_practitioner(clean(prac))


async def _enrich_practitioner(prac: dict) -> dict:
    pid = prac["id"]
    services = await db.services.find({"practitioner_id": pid, "is_active": True}).sort("display_order", 1).to_list(200)
    portfolio = await db.portfolio_items.find({"practitioner_id": pid}).sort("display_order", 1).to_list(200)
    reviews = await db.reviews.find({"practitioner_id": pid, "is_visible": True}).sort("created_at", -1).to_list(100)
    availability = await db.availability.find({"practitioner_id": pid}).to_list(20)
    prac["services"] = clean_list(services)
    prac["portfolio"] = clean_list(portfolio)
    prac["reviews"] = clean_list(reviews)
    prac["availability"] = clean_list(availability)
    return prac


# =====================================================================
# Practitioner — Self management
# =====================================================================
async def _require_practitioner_profile(user: dict) -> dict:
    prac = await db.practitioners.find_one({"user_id": user["id"]})
    if not prac:
        raise HTTPException(status_code=404, detail="Practitioner profile not found")
    return prac


@api.get("/me/practitioner")
async def my_practitioner(user: dict = Depends(get_current_user)):
    if user["role"] != "practitioner":
        raise HTTPException(status_code=403, detail="Practitioner only")
    prac = await db.practitioners.find_one({"user_id": user["id"]})
    if not prac:
        return {"exists": False}
    return {"exists": True, "practitioner": await _enrich_practitioner(clean(prac))}


@api.post("/me/practitioner")
async def upsert_my_practitioner(body: PractitionerUpsertIn, user: dict = Depends(get_current_user)):
    if user["role"] != "practitioner":
        raise HTTPException(status_code=403, detail="Practitioner only")
    existing = await db.practitioners.find_one({"user_id": user["id"]})
    base_slug = (body.display_name or user["name"]).lower().replace(" ", "-")
    base_slug = "".join(ch for ch in base_slug if ch.isalnum() or ch == "-")[:40] or "practitioner"
    if existing:
        slug = existing["direct_booking_slug"]
        update = body.model_dump()
        update["updated_at"] = utcnow_iso()
        await db.practitioners.update_one({"id": existing["id"]}, {"$set": update})
        return {"id": existing["id"], "direct_booking_slug": slug}
    else:
        # ensure slug unique
        slug = base_slug
        i = 1
        while await db.practitioners.find_one({"direct_booking_slug": slug}):
            i += 1
            slug = f"{base_slug}-{i}"
        pid = str(uuid.uuid4())
        doc = {
            "id": pid,
            "user_id": user["id"],
            **body.model_dump(),
            "direct_booking_slug": slug,
            "is_premium": False,
            "is_featured": False,
            "avg_rating": 0.0,
            "total_reviews": 0,
            "created_at": utcnow_iso(),
            "updated_at": utcnow_iso(),
        }
        await db.practitioners.insert_one(doc)
        return {"id": pid, "direct_booking_slug": slug}


# ---- Services CRUD ----
@api.get("/me/services")
async def my_services(user: dict = Depends(get_current_user)):
    prac = await _require_practitioner_profile(user)
    docs = await db.services.find({"practitioner_id": prac["id"]}).to_list(200)
    return clean_list(docs)


@api.post("/me/services")
async def create_service(body: ServiceIn, user: dict = Depends(get_current_user)):
    prac = await _require_practitioner_profile(user)
    cat = await db.service_categories.find_one({"id": body.category_id})
    if not cat:
        raise HTTPException(status_code=400, detail="Invalid category")
    doc = {
        "id": str(uuid.uuid4()),
        "practitioner_id": prac["id"],
        "category_name": cat["name"],
        "is_active": True,
        "display_order": 0,
        "created_at": utcnow_iso(),
        **body.model_dump(),
    }
    await db.services.insert_one(doc)
    return clean(doc)


@api.put("/me/services/{service_id}")
async def update_service(service_id: str, body: ServiceIn, user: dict = Depends(get_current_user)):
    prac = await _require_practitioner_profile(user)
    cat = await db.service_categories.find_one({"id": body.category_id})
    if not cat:
        raise HTTPException(status_code=400, detail="Invalid category")
    res = await db.services.update_one(
        {"id": service_id, "practitioner_id": prac["id"]},
        {"$set": {**body.model_dump(), "category_name": cat["name"]}},
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"ok": True}


@api.delete("/me/services/{service_id}")
async def delete_service(service_id: str, user: dict = Depends(get_current_user)):
    prac = await _require_practitioner_profile(user)
    res = await db.services.delete_one({"id": service_id, "practitioner_id": prac["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"ok": True}


# ---- Portfolio CRUD ----
@api.get("/me/portfolio")
async def my_portfolio(user: dict = Depends(get_current_user)):
    prac = await _require_practitioner_profile(user)
    docs = await db.portfolio_items.find({"practitioner_id": prac["id"]}).sort("display_order", 1).to_list(500)
    return clean_list(docs)


@api.post("/me/portfolio")
async def add_portfolio(body: PortfolioItemIn, user: dict = Depends(get_current_user)):
    prac = await _require_practitioner_profile(user)
    cat = await db.service_categories.find_one({"id": body.category_id})
    if not cat:
        raise HTTPException(status_code=400, detail="Invalid category")
    doc = {
        "id": str(uuid.uuid4()),
        "practitioner_id": prac["id"],
        "category_name": cat["name"],
        "imported_from_instagram": False,
        "display_order": 0,
        "created_at": utcnow_iso(),
        **body.model_dump(),
    }
    await db.portfolio_items.insert_one(doc)
    return clean(doc)


@api.delete("/me/portfolio/{item_id}")
async def delete_portfolio(item_id: str, user: dict = Depends(get_current_user)):
    prac = await _require_practitioner_profile(user)
    res = await db.portfolio_items.delete_one({"id": item_id, "practitioner_id": prac["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    return {"ok": True}


# ---- Availability ----
@api.get("/me/availability")
async def my_availability(user: dict = Depends(get_current_user)):
    prac = await _require_practitioner_profile(user)
    docs = await db.availability.find({"practitioner_id": prac["id"]}).sort("day_of_week", 1).to_list(50)
    return clean_list(docs)


@api.put("/me/availability")
async def set_my_availability(body: List[AvailabilityIn], user: dict = Depends(get_current_user)):
    prac = await _require_practitioner_profile(user)
    await db.availability.delete_many({"practitioner_id": prac["id"]})
    docs = [{"id": str(uuid.uuid4()), "practitioner_id": prac["id"], **a.model_dump()} for a in body]
    if docs:
        await db.availability.insert_many(docs)
    return {"ok": True, "count": len(docs)}


# =====================================================================
# Bookings & Time slot computation
# =====================================================================
def _to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _from_minutes(mins: int) -> str:
    return f"{mins // 60:02d}:{mins % 60:02d}"


@api.get("/practitioners/{practitioner_id}/slots")
async def get_slots(practitioner_id: str, date: str, service_id: str):
    """Return list of available start times (HH:MM) on the given date for the given service."""
    svc = await db.services.find_one({"id": service_id, "practitioner_id": practitioner_id})
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    try:
        the_date = datetime.strptime(date, "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date (YYYY-MM-DD)")
    dow = the_date.weekday()
    avail = await db.availability.find_one({"practitioner_id": practitioner_id, "day_of_week": dow, "is_available": True})
    if not avail:
        return {"date": date, "slots": []}

    start = _to_minutes(avail["start_time"])
    end = _to_minutes(avail["end_time"])
    duration = svc["duration_minutes_min"]

    # existing bookings for that date (block their time)
    bookings = await db.bookings.find({
        "practitioner_id": practitioner_id,
        "booking_date": date,
        "status": {"$in": ["pending", "confirmed"]},
    }).to_list(100)
    blocks = []
    for b in bookings:
        blocks.append((_to_minutes(b["start_time"]), _to_minutes(b["end_time"])))

    slots = []
    step = 30  # 30-min granularity
    t = start
    while t + duration <= end:
        slot_end = t + duration
        # Check overlap
        overlap = any(not (slot_end <= bs or t >= be) for (bs, be) in blocks)
        if not overlap:
            slots.append(_from_minutes(t))
        t += step
    return {"date": date, "slots": slots, "duration_minutes": duration}


@api.post("/bookings")
async def create_booking(body: BookingIn, user: dict = Depends(get_current_user)):
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Only clients can book")
    svc = await db.services.find_one({"id": body.service_id, "practitioner_id": body.practitioner_id})
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    prac = await db.practitioners.find_one({"id": body.practitioner_id})
    if not prac:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    duration = svc["duration_minutes_min"]
    start_min = _to_minutes(body.start_time)
    end_time = _from_minutes(start_min + duration)
    price = float(svc["price_min"])
    deposit = round(price * 0.25, 2)

    # Commission logic
    rel = await db.client_practitioner_relationships.find_one({
        "client_id": user["id"], "practitioner_id": body.practitioner_id
    })
    if rel is None:
        is_first_marketplace = body.client_source == "marketplace"
        commission_rate = 0.10 if is_first_marketplace else 0.0
    else:
        is_first_marketplace = False
        commission_rate = 0.0

    commission_amount = round(price * commission_rate, 2)
    practitioner_payout = round(deposit - commission_amount, 2)

    booking_id = str(uuid.uuid4())
    booking = {
        "id": booking_id,
        "practitioner_id": body.practitioner_id,
        "practitioner_name": prac["display_name"],
        "client_id": user["id"],
        "client_name": user["name"],
        "client_email": user["email"],
        "service_id": body.service_id,
        "service_name": svc["name"],
        "category_name": svc.get("category_name"),
        "status": "confirmed",  # MVP: deposit is mocked as paid, so booking confirmed
        "service_location": body.service_location,
        "client_address": body.client_address,
        "booking_date": body.booking_date,
        "start_time": body.start_time,
        "end_time": end_time,
        "duration_minutes": duration,
        "quoted_price": price,
        "deposit_amount": deposit,
        "deposit_paid": True,  # MOCKED Stripe deposit
        "deposit_stripe_payment_id": f"mock_pi_{uuid.uuid4().hex[:16]}",
        "final_payment_amount": None,
        "final_payment_method": None,
        "client_source": body.client_source,
        "is_first_marketplace_booking": is_first_marketplace,
        "commission_rate": commission_rate,
        "commission_amount": commission_amount,
        "practitioner_payout_amount": practitioner_payout,
        "payout_status": "pending",
        "client_notes": body.client_notes,
        "practitioner_notes": None,
        "created_at": utcnow_iso(),
        "updated_at": utcnow_iso(),
    }
    await db.bookings.insert_one(booking)

    # Upsert relationship
    if rel is None:
        await db.client_practitioner_relationships.insert_one({
            "id": str(uuid.uuid4()),
            "client_id": user["id"],
            "practitioner_id": body.practitioner_id,
            "source": body.client_source,
            "first_booking_id": booking_id,
            "first_booking_date": body.booking_date,
            "total_bookings": 1,
            "is_commission_eligible": is_first_marketplace,
            "created_at": utcnow_iso(),
        })
    else:
        await db.client_practitioner_relationships.update_one(
            {"id": rel["id"]}, {"$inc": {"total_bookings": 1}}
        )

    # Mock notification log
    await db.notifications.insert_many([
        {
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "channel": "sms+whatsapp",
            "body": f"Your booking with {prac['display_name']} for {svc['name']} on {body.booking_date} at {body.start_time} is confirmed. Deposit: ${deposit:.2f}.",
            "created_at": utcnow_iso(),
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": prac["user_id"],
            "channel": "sms+whatsapp",
            "body": f"New booking! {user['name']} booked {svc['name']} on {body.booking_date} at {body.start_time}. Deposit received: ${deposit:.2f}. {'Marketplace (10% commission)' if is_first_marketplace else ('Direct link client' if body.client_source == 'direct_link' else 'Repeat client (0% commission)')}.",
            "created_at": utcnow_iso(),
        },
    ])

    return clean(booking)


@api.get("/bookings")
async def list_bookings(user: dict = Depends(get_current_user)):
    if user["role"] == "client":
        q = {"client_id": user["id"]}
    elif user["role"] == "practitioner":
        prac = await db.practitioners.find_one({"user_id": user["id"]})
        if not prac:
            return []
        q = {"practitioner_id": prac["id"]}
    else:  # admin
        q = {}
    docs = await db.bookings.find(q).sort("booking_date", -1).to_list(500)
    return clean_list(docs)


@api.get("/bookings/{booking_id}")
async def get_booking(booking_id: str, user: dict = Depends(get_current_user)):
    b = await db.bookings.find_one({"id": booking_id})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    # Authorization
    if user["role"] == "client" and b["client_id"] != user["id"]:
        raise HTTPException(status_code=403)
    if user["role"] == "practitioner":
        prac = await db.practitioners.find_one({"user_id": user["id"]})
        if not prac or b["practitioner_id"] != prac["id"]:
            raise HTTPException(status_code=403)
    return clean(b)


class BookingStatusIn(BaseModel):
    status: Literal["confirmed", "completed", "cancelled_by_client", "cancelled_by_practitioner", "no_show"]
    practitioner_notes: Optional[str] = None


@api.put("/bookings/{booking_id}/status")
async def update_booking_status(booking_id: str, body: BookingStatusIn, user: dict = Depends(get_current_user)):
    b = await db.bookings.find_one({"id": booking_id})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    if user["role"] == "client":
        if b["client_id"] != user["id"]:
            raise HTTPException(status_code=403)
        if body.status not in ("cancelled_by_client",):
            raise HTTPException(status_code=403, detail="Clients can only cancel")
    elif user["role"] == "practitioner":
        prac = await db.practitioners.find_one({"user_id": user["id"]})
        if not prac or b["practitioner_id"] != prac["id"]:
            raise HTTPException(status_code=403)
    update = {"status": body.status, "updated_at": utcnow_iso()}
    if body.practitioner_notes is not None:
        update["practitioner_notes"] = body.practitioner_notes
    if body.status == "completed":
        update["payout_status"] = "paid"
    await db.bookings.update_one({"id": booking_id}, {"$set": update})
    return {"ok": True}


# =====================================================================
# Reviews
# =====================================================================
@api.post("/reviews")
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
    # Recompute aggregates
    revs = await db.reviews.find({"practitioner_id": b["practitioner_id"], "is_visible": True}).to_list(500)
    avg = sum(r["rating"] for r in revs) / len(revs)
    await db.practitioners.update_one(
        {"id": b["practitioner_id"]},
        {"$set": {"avg_rating": round(avg, 2), "total_reviews": len(revs)}},
    )
    return clean(doc)


# =====================================================================
# Favorites
# =====================================================================
class FavoriteIn(BaseModel):
    practitioner_id: str


@api.get("/me/favorites")
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


@api.post("/me/favorites")
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


@api.delete("/me/favorites/{practitioner_id}")
async def remove_favorite(practitioner_id: str, user: dict = Depends(get_current_user)):
    await db.favorites.delete_one({"client_id": user["id"], "practitioner_id": practitioner_id})
    return {"ok": True}


# =====================================================================
# Practitioner dashboard
# =====================================================================
@api.get("/me/practitioner/dashboard")
async def practitioner_dashboard(user: dict = Depends(get_current_user)):
    if user["role"] != "practitioner":
        raise HTTPException(status_code=403)
    prac = await db.practitioners.find_one({"user_id": user["id"]})
    if not prac:
        return {"exists": False}
    bookings = await db.bookings.find({"practitioner_id": prac["id"]}).to_list(500)
    gross = sum(b["quoted_price"] for b in bookings if b["status"] in ("confirmed", "completed"))
    commission = sum(b["commission_amount"] for b in bookings if b["status"] in ("confirmed", "completed"))
    deposits_collected = sum(b["deposit_amount"] for b in bookings if b["deposit_paid"])
    net_payout = deposits_collected - commission
    upcoming = [b for b in bookings if b["status"] in ("confirmed", "pending")]
    completed = [b for b in bookings if b["status"] == "completed"]
    return {
        "exists": True,
        "stats": {
            "total_bookings": len(bookings),
            "upcoming_bookings": len(upcoming),
            "completed_bookings": len(completed),
            "gross_gmv": round(gross, 2),
            "total_commission": round(commission, 2),
            "deposits_collected": round(deposits_collected, 2),
            "net_payout": round(net_payout, 2),
            "avg_rating": prac.get("avg_rating", 0),
            "total_reviews": prac.get("total_reviews", 0),
            "direct_booking_slug": prac["direct_booking_slug"],
        },
        "upcoming": clean_list(sorted(upcoming, key=lambda x: (x["booking_date"], x["start_time"]))[:10]),
    }


# =====================================================================
# Admin
# =====================================================================
@api.get("/admin/stats")
async def admin_stats(user: dict = Depends(require_role("admin"))):
    total_practitioners = await db.practitioners.count_documents({})
    total_clients = await db.users.count_documents({"role": "client"})
    bookings = await db.bookings.find({}).to_list(1000)
    gmv = sum(b["quoted_price"] for b in bookings if b["status"] in ("confirmed", "completed"))
    commission = sum(b["commission_amount"] for b in bookings if b["status"] in ("confirmed", "completed"))
    by_type = {}
    pracs = await db.practitioners.find({}).to_list(500)
    for p in pracs:
        by_type[p["practitioner_type"]] = by_type.get(p["practitioner_type"], 0) + 1
    return {
        "total_practitioners": total_practitioners,
        "total_clients": total_clients,
        "total_bookings": len(bookings),
        "gmv": round(gmv, 2),
        "commission_revenue": round(commission, 2),
        "practitioners_by_type": by_type,
        "recent_bookings": clean_list(sorted(bookings, key=lambda x: x["created_at"], reverse=True)[:15]),
    }


# =====================================================================
# Notifications (mocked)
# =====================================================================
@api.get("/me/notifications")
async def my_notifications(user: dict = Depends(get_current_user)):
    docs = await db.notifications.find({"user_id": user["id"]}).sort("created_at", -1).to_list(100)
    return clean_list(docs)


# Mount router and middleware
app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# Startup
# =====================================================================
@app.on_event("startup")
async def on_startup():
    await db.users.create_index("email", unique=True)
    await db.practitioners.create_index("direct_booking_slug", unique=True, sparse=True)
    await db.practitioners.create_index("city")
    await db.services.create_index("practitioner_id")
    await db.portfolio_items.create_index("practitioner_id")
    await db.bookings.create_index([("practitioner_id", 1), ("booking_date", 1)])
    await db.bookings.create_index("client_id")
    from seed import run_all_seeds
    await run_all_seeds(db)
    logger.info("Curlnect startup complete — seeds loaded.")


@app.on_event("shutdown")
async def on_shutdown():
    client.close()


@api.get("/")
async def root():
    return {"app": "Curlnect", "status": "ok"}
