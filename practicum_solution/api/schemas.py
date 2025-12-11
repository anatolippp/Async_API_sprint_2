from pydantic import BaseModel, Field


class LikePayload(BaseModel):
    movie_id: str
    score: int = Field(ge=0, le=10)


class ReviewPayload(BaseModel):
    movie_id: str
    text: str
    score: int = Field(ge=0, le=10)


class BookmarkPayload(BaseModel):
    movie_id: str
