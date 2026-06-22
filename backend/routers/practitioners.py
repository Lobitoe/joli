"""Practitioners router: public discovery + practitioner self-management."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from db import db
from schemas import (
    PractitionerUpsertIn,
    ServiceIn,
    PortfolioItemIn,
    AvailabilityIn,
)
from utils import (
    clean,
    clean_list,
    enrich_practitioner,
    require_practitioner_profile,
    utcnow_iso,
)

router = APIRouter(tags=["practitioners"])


# -------- Public discovery --------
@router.get("/practitioners")
async def list_practitioners(
    city: Optional[str] = None,
    category: Optional[str] = None,  # category name OR id
    service_mode: Optional[str] = None,  # clients_come_to_me | i_travel_to_clients | both
    practitioner_type: Optional[str] = None,
):
    q: dict = {"is_suspended": {"$ne": True}}
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

    if category:
        cat = await db.service_categories.find_one({
            "$or": [{"id": category}, {"name": {"$regex": f"^{category}$", "$options": "i"}}]
        })
        if cat:
            ids_with_cat = await db.services.distinct(
                "practitioner_id", {"category_id": cat["id"], "is_active": True}
            )
            practitioners = [p for p in practitioners if p["id"] in ids_with_cat]
        else:
            practitioners = []

    for p in practitioners:
        thumbs = await db.portfolio_items.find({"practitioner_id": p["id"]}).limit(4).to_list(4)
        p["portfolio_thumbs"] = [t["image_url"] for t in thumbs]
        services = await db.services.find({"practitioner_id": p["id"], "is_active": True}).to_list(100)
        p["service_count"] = len(services)
        p["starting_price"] = min([s["price_min"] for s in services], default=None)
        badges = await db.practitioner_badges.find({"practitioner_id": p["id"], "is_active": True}).to_list(20)
        p["badges"] = [b["badge_type"] for b in badges]
    return practitioners


@router.get("/practitioners/{practitioner_id}")
async def get_practitioner(practitioner_id: str):
    prac = await db.practitioners.find_one({"id": practitioner_id})
    if not prac:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return await enrich_practitioner(clean(prac))


@router.get("/practitioners/slug/{slug}")
async def get_practitioner_by_slug(slug: str):
    prac = await db.practitioners.find_one({"direct_booking_slug": slug})
    if not prac:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return await enrich_practitioner(clean(prac))


# -------- Practitioner self-management --------
@router.get("/me/practitioner")
async def my_practitioner(user: dict = Depends(get_current_user)):
    if user["role"] != "practitioner":
        raise HTTPException(status_code=403, detail="Practitioner only")
    prac = await db.practitioners.find_one({"user_id": user["id"]})
    if not prac:
        return {"exists": False}
    return {"exists": True, "practitioner": await enrich_practitioner(clean(prac))}


@router.post("/me/practitioner")
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


# -------- Services CRUD --------
@router.get("/me/services")
async def my_services(user: dict = Depends(get_current_user)):
    prac = await require_practitioner_profile(user)
    docs = await db.services.find({"practitioner_id": prac["id"]}).to_list(200)
    return clean_list(docs)


@router.post("/me/services")
async def create_service(body: ServiceIn, user: dict = Depends(get_current_user)):
    prac = await require_practitioner_profile(user)
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


@router.put("/me/services/{service_id}")
async def update_service(service_id: str, body: ServiceIn, user: dict = Depends(get_current_user)):
    prac = await require_practitioner_profile(user)
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


@router.delete("/me/services/{service_id}")
async def delete_service(service_id: str, user: dict = Depends(get_current_user)):
    prac = await require_practitioner_profile(user)
    res = await db.services.delete_one({"id": service_id, "practitioner_id": prac["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"ok": True}


# -------- Portfolio CRUD --------
@router.get("/me/portfolio")
async def my_portfolio(user: dict = Depends(get_current_user)):
    prac = await require_practitioner_profile(user)
    docs = await db.portfolio_items.find({"practitioner_id": prac["id"]}).sort("display_order", 1).to_list(500)
    return clean_list(docs)


@router.post("/me/portfolio")
async def add_portfolio(body: PortfolioItemIn, user: dict = Depends(get_current_user)):
    prac = await require_practitioner_profile(user)
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


@router.delete("/me/portfolio/{item_id}")
async def delete_portfolio(item_id: str, user: dict = Depends(get_current_user)):
    prac = await require_practitioner_profile(user)
    res = await db.portfolio_items.delete_one({"id": item_id, "practitioner_id": prac["id"]})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    return {"ok": True}


# -------- Availability --------
@router.get("/me/availability")
async def my_availability(user: dict = Depends(get_current_user)):
    prac = await require_practitioner_profile(user)
    docs = await db.availability.find({"practitioner_id": prac["id"]}).sort("day_of_week", 1).to_list(50)
    return clean_list(docs)


@router.put("/me/availability")
async def set_my_availability(body: List[AvailabilityIn], user: dict = Depends(get_current_user)):
    prac = await require_practitioner_profile(user)
    await db.availability.delete_many({"practitioner_id": prac["id"]})
    docs = [{"id": str(uuid.uuid4()), "practitioner_id": prac["id"], **a.model_dump()} for a in body]
    if docs:
        await db.availability.insert_many(docs)
    return {"ok": True, "count": len(docs)}


# -------- Practitioner dashboard --------
@router.get("/me/practitioner/dashboard")
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
