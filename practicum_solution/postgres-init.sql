create table if not exists likes (
    user_id varchar(36),
    movie_id varchar(36),
    score smallint,
    updated_at timestamp,
    primary key (user_id, movie_id)
);
create index if not exists idx_likes_movie on likes (movie_id);

create table if not exists bookmarks (
    user_id varchar(36),
    movie_id varchar(36),
    created_at timestamp,
    primary key (user_id, movie_id)
);
create index if not exists idx_bookmarks_user on bookmarks (user_id);

create table if not exists reviews (
    id serial primary key,
    user_id varchar(36),
    movie_id varchar(36),
    text text,
    created_at timestamp,
    likes integer default 0,
    dislikes integer default 0,
    score smallint
);
create index if not exists idx_reviews_movie on reviews (movie_id);
create index if not exists idx_reviews_movie_likes on reviews (movie_id, likes desc);
