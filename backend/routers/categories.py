"""Categories router: simple list endpoint for service taxonomy."""
from fastapi import APIRouter

from db import db
from utils import clean_list

router = APIRouter(tags=["categories"])


@router.get("/categories")
async def list_categories():
    docs = await db.service_categories.find({"is_active": True}).sort("display_order", 1).to_list(500)
    return clean_list(docs)
