from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None

def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.MONGO_URI)
    return client

def get_db():
    return get_client()[settings.MONGO_DB]

def users_col():
    return get_db()["users"]

def interviews_col():
    return get_db()["interviews"]  # ✅ fixed to call get_db()

def user_profiles_col():
    return get_db()["user_profiles"]

def applications_col():
    return get_db()["applications"]
