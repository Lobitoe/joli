"""Admin router: stats, users, activity feed, suspend toggle, notifications."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user, require_role
from db import db
from schemas import SuspendPractitionerIn
from utils import clean_list, utcnow_iso

router = APIRouter(tags=["admin"])


# -------- Stats --------
@router.get("/admin/stats")
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


# -------- Users --------
@router.get("/admin/users")
async def admin_list_users(
    user: dict = Depends(require_role("admin")),
    role: Optional[str] = None,
    search: Optional[str] = None,
):
    q: dict = {}
    if role:
        q["role"] = role
    if search:
        q["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}},
        ]
    users = await db.users.find(q, {"password_hash": 0}).sort("created_at", -1).to_list(500)
    users = clean_list(users)
    for u in users:
        u["bookings_count"] = 0
        if u["role"] == "practitioner":
            prac = await db.practitioners.find_one({"user_id": u["id"]})
            if prac:
                u["practitioner_id"] = prac["id"]
                u["practitioner_display_name"] = prac.get("display_name")
                u["verification_status"] = prac.get("verification_status", "unverified")
                u["is_suspended"] = prac.get("is_suspended", False)
                u["avg_rating"] = prac.get("avg_rating", 0)
                u["total_reviews"] = prac.get("total_reviews", 0)
                u["bookings_count"] = await db.bookings.count_documents({"practitioner_id": prac["id"]})
        elif u["role"] == "client":
            u["bookings_count"] = await db.bookings.count_documents({"client_id": u["id"]})
    return users


@router.put("/admin/practitioners/{practitioner_id}/suspend")
async def admin_toggle_suspend(
    practitioner_id: str,
    body: SuspendPractitionerIn,
    user: dict = Depends(require_role("admin")),
):
    prac = await db.practitioners.find_one({"id": practitioner_id})
    if not prac:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    await db.practitioners.update_one(
        {"id": practitioner_id},
        {"$set": {
            "is_suspended": body.suspended,
            "suspension_reason": body.reason if body.suspended else None,
            "suspended_at": utcnow_iso() if body.suspended else None,
        }},
    )
    return {"ok": True, "is_suspended": body.suspended}


# -------- Activity feed --------
@router.get("/admin/activity")
async def admin_activity_feed(user: dict = Depends(require_role("admin"))):
    items = []

    new_users = await db.users.find({}, {"password_hash": 0}).sort("created_at", -1).limit(15).to_list(15)
    for u in new_users:
        items.append({
            "kind": "user_joined",
            "at": u["created_at"],
            "summary": f"{u['name']} joined as {u['role']}",
            "user_id": u["id"],
            "user_role": u["role"],
        })

    recent_bookings = await db.bookings.find({}).sort("created_at", -1).limit(20).to_list(20)
    for b in recent_bookings:
        items.append({
            "kind": "booking_created",
            "at": b["created_at"],
            "summary": f"{b['client_name']} booked {b['service_name']} with {b['practitioner_name']} ({b['client_source']})",
            "booking_id": b["id"],
            "amount": b["quoted_price"],
            "commission": b["commission_amount"],
            "status": b["status"],
        })

    recent_reviews = await db.reviews.find({}).sort("created_at", -1).limit(10).to_list(10)
    for r in recent_reviews:
        prac = await db.practitioners.find_one({"id": r["practitioner_id"]})
        items.append({
            "kind": "review_posted",
            "at": r["created_at"],
            "summary": f"{r['client_name']} rated {prac['display_name'] if prac else 'practitioner'} {r['rating']}★",
            "rating": r["rating"],
            "review_id": r["id"],
        })

    recent_verifs = await db.practitioner_verifications.find({}).sort("created_at", -1).limit(10).to_list(10)
    for v in recent_verifs:
        prac = await db.practitioners.find_one({"id": v["practitioner_id"]})
        items.append({
            "kind": "verification_submitted",
            "at": v["created_at"],
            "summary": f"{prac['display_name'] if prac else 'Practitioner'} submitted {v['verification_type'].replace('_', ' ')} → {v['status']}",
            "verification_id": v["id"],
            "verification_status": v["status"],
        })

    items.sort(key=lambda x: x["at"], reverse=True)
    return items[:50]


# -------- Notifications (mocked) --------
@router.get("/me/notifications")
async def my_notifications(user: dict = Depends(get_current_user)):
    docs = await db.notifications.find({"user_id": user["id"]}).sort("created_at", -1).to_list(100)
    return clean_list(docs)
