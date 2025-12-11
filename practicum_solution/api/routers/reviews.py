from typing import Any, Dict, List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from ..dependencies import get_current_user, get_db, serialize_document
from ..schemas import ReviewPayload

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewPayload,
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    doc = {
        "user_id": user_id,
        "movie_id": payload.movie_id,
        "text": payload.text,
        "likes": 0,
        "dislikes": 0,
        "score": payload.score,
    }
    result = await db.reviews.insert_one(doc)
    return {"id": str(result.inserted_id), **doc}


@router.post("/{review_id}/vote")
async def vote_review(
    review_id: str,
    like: bool = Query(default=True),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    field = "likes" if like else "dislikes"
    updated = await db.reviews.find_one_and_update(
        {"_id": ObjectId(review_id)}, {"$inc": {field: 1}}, return_document=ReturnDocument.AFTER
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return {"id": review_id, field: updated[field]}


@router.get("")
async def list_reviews(
    movie_id: str,
    sort_by: str = Query(default="likes", enum=["likes", "dislikes", "score"]),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> List[Dict[str, Any]]:
    cursor = db.reviews.find({"movie_id": movie_id}).sort(sort_by, -1)
    return [serialize_document(doc) async for doc in cursor]
