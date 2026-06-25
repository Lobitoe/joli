"""Shared Mongo client/db, isolated from server.py to avoid circular imports."""
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

_mongo_url = os.environ["MONGO_URL"]
_db_name = os.environ["DB_NAME"]

# Use certifi's CA bundle for the TLS handshake. Fixes MongoDB Atlas SSL
# handshake failures on cloud hosts (Render/Heroku/Lambda, etc.) whose system
# CA store is missing or stale.
client = AsyncIOMotorClient(_mongo_url, tlsCAFile=certifi.where())
db = client[_db_name]
