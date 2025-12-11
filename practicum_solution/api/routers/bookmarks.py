from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..dependencies import get_current_user, get_db, serialize_document
from ..schemas import BookmarkPayload

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_bookmark(
    payload: BookmarkPayload,
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    await db.bookmarks.update_one(
        {"user_id": user_id, "movie_id": payload.movie_id},
        {"$set": {"user_id": user_id, "movie_id": payload.movie_id}},
        upsert=True,
    )
    return {"user_id": user_id, "movie_id": payload.movie_id}


@router.delete("/{movie_id}")
async def remove_bookmark(
    movie_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, str]:
    result = await db.bookmarks.delete_one({"user_id": user_id, "movie_id": movie_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    return {"status": "deleted", "movie_id": movie_id}


@router.get("")
async def list_bookmarks(
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> List[Dict[str, Any]]:
    cursor = db.bookmarks.find({"user_id": user_id}).sort("_id", 1)
    return [serialize_document(doc) async for doc in cursor]
