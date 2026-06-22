"""Verifications & badges router (practitioner self + admin approve/reject queue)."""
import uuid
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user, require_role
from db import db
from schemas import VerificationIn, VerificationDecisionIn
from utils import clean_list, utcnow_iso

router = APIRouter(tags=["verifications"])


@router.post("/me/practitioner/verifications")
async def submit_verification(body: VerificationIn, user: dict = Depends(get_current_user)):
    if user["role"] != "practitioner":
        raise HTTPException(status_code=403)
    prac = await db.practitioners.find_one({"user_id": user["id"]})
    if not prac:
        raise HTTPException(status_code=404, detail="Practitioner profile not found")
    existing = await db.practitioner_verifications.find_one({
        "practitioner_id": prac["id"], "verification_type": body.verification_type
    })
    doc = {
        "verification_type": body.verification_type,
        "document_url": body.document_url,
        "document_expiry": body.document_expiry,
        "status": "pending",
        "verified_by": None,
        "verified_at": None,
        "rejection_reason": None,
        "updated_at": utcnow_iso(),
    }
    if existing:
        await db.practitioner_verifications.update_one({"id": existing["id"]}, {"$set": doc})
        return {"ok": True, "status": "pending"}
    doc.update({"id": str(uuid.uuid4()), "practitioner_id": prac["id"], "created_at": utcnow_iso()})
    await db.practitioner_verifications.insert_one(doc)
    return {"ok": True, "status": "pending"}


@router.get("/me/practitioner/verifications")
async def my_verifications(user: dict = Depends(get_current_user)):
    if user["role"] != "practitioner":
        raise HTTPException(status_code=403)
    prac = await db.practitioners.find_one({"user_id": user["id"]})
    if not prac:
        return []
    docs = await db.practitioner_verifications.find({"practitioner_id": prac["id"]}).to_list(20)
    badges = await db.practitioner_badges.find({"practitioner_id": prac["id"], "is_active": True}).to_list(20)
    return {
        "verifications": clean_list(docs),
        "badges": [b["badge_type"] for b in badges],
        "verification_status": prac.get("verification_status", "unverified"),
    }


@router.put("/admin/verifications/{verification_id}")
async def decide_verification(
    verification_id: str,
    body: VerificationDecisionIn,
    user: dict = Depends(require_role("admin")),
):
    v = await db.practitioner_verifications.find_one({"id": verification_id})
    if not v:
        raise HTTPException(status_code=404, detail="Verification not found")
    update = {
        "status": body.decision,
        "verified_by": user["id"],
        "verified_at": utcnow_iso(),
        "rejection_reason": body.rejection_reason if body.decision == "rejected" else None,
        "updated_at": utcnow_iso(),
    }
    await db.practitioner_verifications.update_one({"id": verification_id}, {"$set": update})
    if body.decision == "verified":
        for badge_type in body.grant_badges:
            existing = await db.practitioner_badges.find_one({
                "practitioner_id": v["practitioner_id"], "badge_type": badge_type
            })
            if existing:
                continue
            await db.practitioner_badges.insert_one({
                "id": str(uuid.uuid4()),
                "practitioner_id": v["practitioner_id"],
                "badge_type": badge_type,
                "is_active": True,
                "granted_at": utcnow_iso(),
                "expires_at": None,
            })
        gov = await db.practitioner_verifications.find_one({
            "practitioner_id": v["practitioner_id"],
            "verification_type": "government_id",
            "status": "verified",
        })
        if gov:
            await db.practitioners.update_one(
                {"id": v["practitioner_id"]}, {"$set": {"verification_status": "verified"}}
            )
        if "insured" in body.grant_badges:
            await db.practitioners.update_one(
                {"id": v["practitioner_id"]}, {"$set": {"is_insured": True}}
            )
    return {"ok": True}


@router.get("/admin/verifications")
async def list_pending_verifications(user: dict = Depends(require_role("admin"))):
    docs = await db.practitioner_verifications.find({"status": "pending"}).sort("created_at", 1).to_list(200)
    docs = clean_list(docs)
    for d in docs:
        prac = await db.practitioners.find_one({"id": d["practitioner_id"]})
        u = await db.users.find_one({"id": prac["user_id"]}) if prac else None
        d["practitioner_name"] = prac["display_name"] if prac else None
        d["practitioner_type"] = prac["practitioner_type"] if prac else None
        d["practitioner_email"] = u["email"] if u else None
    return docs
