from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..dependencies import get_db

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/{movie_id}/rating")
async def movie_rating(movie_id: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> Dict[str, Any]:
    pipeline = [
        {"$match": {"movie_id": movie_id}},
        {"$group": {"_id": "$movie_id", "avg": {"$avg": "$score"}, "count": {"$sum": 1}}},
    ]
    result = await db.likes.aggregate(pipeline).to_list(1)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie has no votes")
    stats = result[0]
    return {"movie_id": movie_id, "avg_score": round(stats.get("avg", 0), 2), "votes": stats.get("count", 0)}
