from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..dependencies import get_current_user, get_db, serialize_document
from ..schemas import LikePayload

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def upsert_like(
    payload: LikePayload,
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    await db.likes.update_one(
        {"user_id": user_id, "movie_id": payload.movie_id},
        {"$set": {"score": payload.score}},
        upsert=True,
    )
    return {"user_id": user_id, "movie_id": payload.movie_id, "score": payload.score}


@router.delete("/{movie_id}")
async def delete_like(
    movie_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    result = await db.likes.delete_one({"user_id": user_id, "movie_id": movie_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")
    return {"status": "deleted", "movie_id": movie_id}


@router.get("", response_model=List[Dict[str, Any]])
async def list_likes(
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> List[Dict[str, Any]]:
    cursor = db.likes.find({"user_id": user_id})
    return [serialize_document(doc) async for doc in cursor]
