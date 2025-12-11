from fastapi import Depends, Header, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_db(request: Request) -> AsyncIOMotorDatabase:
    db: AsyncIOMotorDatabase | None = getattr(request.app.state, "db", None)
    if db is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not initialized")
    return db


def serialize_document(document: dict) -> dict:
    normalized = {**document}
    if "_id" in normalized:
        normalized["id"] = str(normalized.pop("_id"))
    return normalized


async def get_user_id(x_user_id: str | None = Header(default="demo-user")) -> str:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User id is required")
    return x_user_id


def get_current_user(user_id: str = Depends(get_user_id)) -> str:
    return user_id
