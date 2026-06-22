"""Blog router: list + detail with embedded practitioner cards."""
from typing import Optional
from fastapi import APIRouter, HTTPException

from db import db
from utils import clean, clean_list

router = APIRouter(tags=["blog"])


@router.get("/blog")
async def list_blog_posts(city: Optional[str] = None, category: Optional[str] = None):
    q = {"is_published": True}
    if city:
        q["city"] = {"$regex": f"^{city}$", "$options": "i"}
    if category:
        q["category"] = category
    docs = await db.blog_posts.find(q).sort("published_at", -1).to_list(100)
    docs = clean_list(docs)
    for d in docs:
        d.pop("body_markdown", None)
    return docs


@router.get("/blog/{slug}")
async def get_blog_post(slug: str):
    doc = await db.blog_posts.find_one({"slug": slug, "is_published": True})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    doc = clean(doc)
    embed = []
    for pid in doc.get("embedded_practitioner_ids", []):
        prac = await db.practitioners.find_one({"id": pid})
        if not prac:
            continue
        prac = clean(prac)
        thumbs = await db.portfolio_items.find({"practitioner_id": pid}).limit(4).to_list(4)
        services = await db.services.find({"practitioner_id": pid, "is_active": True}).to_list(50)
        badges = await db.practitioner_badges.find({"practitioner_id": pid, "is_active": True}).to_list(20)
        prac["portfolio_thumbs"] = [t["image_url"] for t in thumbs]
        prac["starting_price"] = min([s["price_min"] for s in services], default=None)
        prac["service_count"] = len(services)
        prac["badges"] = [b["badge_type"] for b in badges]
        embed.append(prac)
    doc["embedded_practitioners"] = embed
    return doc
