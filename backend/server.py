"""Joli FastAPI server — slim entrypoint that wires routers + lifecycle."""
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import logging
import os
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from db import db, client
from routers.auth_router import router as auth_router
from routers.categories import router as categories_router
from routers.practitioners import router as practitioners_router
from routers.bookings import router as bookings_router
from routers.reviews import router as reviews_router
from routers.favorites import router as favorites_router
from routers.verifications import router as verifications_router
from routers.blog import router as blog_router
from routers.admin import router as admin_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("joli")

app = FastAPI(title="Joli API")

# All routes under /api
api = APIRouter(prefix="/api")
api.include_router(auth_router)
api.include_router(categories_router)
api.include_router(practitioners_router)
api.include_router(bookings_router)
api.include_router(reviews_router)
api.include_router(favorites_router)
api.include_router(verifications_router)
api.include_router(blog_router)
api.include_router(admin_router)


@api.get("/")
async def root():
    return {"app": "Joli", "status": "ok"}


app.include_router(api)

# CORS origins are configurable via the CORS_ORIGINS env var
# (comma-separated). Defaults to "*" so nothing breaks before the
# domain is set; tighten to your domain(s) in production.
_cors_env = os.environ.get("CORS_ORIGINS", "*").strip()
_allow_origins = ["*"] if _cors_env == "*" else [o.strip() for o in _cors_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await db.users.create_index("email", unique=True)
    await db.practitioners.create_index("direct_booking_slug", unique=True, sparse=True)
    await db.practitioners.create_index("city")
    await db.services.create_index("practitioner_id")
    await db.portfolio_items.create_index("practitioner_id")
    await db.bookings.create_index([("practitioner_id", 1), ("booking_date", 1)])
    await db.bookings.create_index("client_id")
    await db.blog_posts.create_index("slug", unique=True, sparse=True)
    await db.blog_posts.create_index([("published_at", -1)])
    # Seeding is idempotent (each seeder guards against duplicates).
    # Controlled by SEED_ON_START (default "true") so you can turn it
    # off later once your database is populated.
    if os.environ.get("SEED_ON_START", "true").strip().lower() in ("1", "true", "yes"):
        from seed import run_all_seeds
        await run_all_seeds(db)
        logger.info("Joli startup complete — seeds loaded.")
    else:
        logger.info("Joli startup complete — seeding skipped (SEED_ON_START=false).")


@app.on_event("shutdown")
async def on_shutdown():
    client.close()
