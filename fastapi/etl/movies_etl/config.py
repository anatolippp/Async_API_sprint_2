from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Postgres
    pg_host: str = Field("localhost", alias="PG_HOST")
    pg_port: int = Field(5432, alias="PG_PORT")
    pg_db: str = Field(..., alias="PG_DB")
    pg_user: str = Field(..., alias="PG_USER")
    pg_password: str = Field(..., alias="PG_PASSWORD")

    # Elasticsearch
    es_url: str = Field("http://localhost:9200", alias="ES_URL")
    es_movies_index: str = Field("movies", alias="ES_MOVIES_INDEX")
    es_genres_index: str = Field("genres", alias="ES_GENRES_INDEX")
    es_persons_index: str = Field("persons", alias="ES_PERSONS_INDEX")

    # ETL
    batch_size: int = Field(200, alias="BATCH_SIZE")
    state_file: str = Field(".state.json", alias="STATE_FILE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ESFilmPerson(BaseModel):
    id: str
    name: str


class ESGenre(BaseModel):
    id: str
    name: str
    description: str | None = None


class ESFilm(BaseModel):
    id: str
    imdb_rating: float | None = None
    genres: list[ESGenre] = Field(default_factory=list)
    genre_names: list[str] = Field(default_factory=list)
    title: str | None = None
    description: str | None = None
    directors_names: list[str] = Field(default_factory=list)
    actors_names: list[str] = Field(default_factory=list)
    writers_names: list[str] = Field(default_factory=list)
    directors: list[ESFilmPerson] = Field(default_factory=list)
    actors: list[ESFilmPerson] = Field(default_factory=list)
    writers: list[ESFilmPerson] = Field(default_factory=list)


class ESPerson(BaseModel):
    id: str
    full_name: str
    