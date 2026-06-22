"""Bookings router: time-slot computation, booking create/list/status."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from db import db
from schemas import BookingIn, BookingStatusIn
from utils import clean, clean_list, from_minutes, to_minutes, utcnow_iso

router = APIRouter(tags=["bookings"])


@router.get("/practitioners/{practitioner_id}/slots")
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
    avail = await db.availability.find_one({
        "practitioner_id": practitioner_id, "day_of_week": dow, "is_available": True
    })
    if not avail:
        return {"date": date, "slots": []}

    start = to_minutes(avail["start_time"])
    end = to_minutes(avail["end_time"])
    duration = svc["duration_minutes_min"]

    bookings = await db.bookings.find({
        "practitioner_id": practitioner_id,
        "booking_date": date,
        "status": {"$in": ["pending", "confirmed"]},
    }).to_list(100)
    blocks = [(to_minutes(b["start_time"]), to_minutes(b["end_time"])) for b in bookings]

    slots = []
    step = 30
    t = start
    while t + duration <= end:
        slot_end = t + duration
        overlap = any(not (slot_end <= bs or t >= be) for (bs, be) in blocks)
        if not overlap:
            slots.append(from_minutes(t))
        t += step
    return {"date": date, "slots": slots, "duration_minutes": duration}


@router.post("/bookings")
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
    start_min = to_minutes(body.start_time)
    end_time = from_minutes(start_min + duration)
    price = float(svc["price_min"])
    deposit = round(price * 0.25, 2)

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
        "status": "confirmed",
        "service_location": body.service_location,
        "client_address": body.client_address,
        "booking_date": body.booking_date,
        "start_time": body.start_time,
        "end_time": end_time,
        "duration_minutes": duration,
        "quoted_price": price,
        "deposit_amount": deposit,
        "deposit_paid": True,
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


@router.get("/bookings")
async def list_bookings(user: dict = Depends(get_current_user)):
    if user["role"] == "client":
        q = {"client_id": user["id"]}
    elif user["role"] == "practitioner":
        prac = await db.practitioners.find_one({"user_id": user["id"]})
        if not prac:
            return []
        q = {"practitioner_id": prac["id"]}
    else:
        q = {}
    docs = await db.bookings.find(q).sort("booking_date", -1).to_list(500)
    return clean_list(docs)


@router.get("/bookings/{booking_id}")
async def get_booking(booking_id: str, user: dict = Depends(get_current_user)):
    b = await db.bookings.find_one({"id": booking_id})
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    if user["role"] == "client" and b["client_id"] != user["id"]:
        raise HTTPException(status_code=403)
    if user["role"] == "practitioner":
        prac = await db.practitioners.find_one({"user_id": user["id"]})
        if not prac or b["practitioner_id"] != prac["id"]:
            raise HTTPException(status_code=403)
    return clean(b)


@router.put("/bookings/{booking_id}/status")
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
