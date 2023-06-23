CREATE DATABASE barhive;

-- DROP TABLES IF THEY EXIST TO PREVENT ERRORS
DROP TABLE IF EXISTS post CASCADE;
DROP TABLE IF EXISTS user_likes;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS follower;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS business_items;
DROP TABLE IF EXISTS "user" CASCADE;

-- WAIT TO ADD TABLES UNTIL AFTER THE DATABASE IS CREATED

CREATE TABLE "user" (
    user_id INTEGER NOT NULL,
    username VARCHAR(80) NOT NULL,
    password VARCHAR(80),
    first_name VARCHAR(80),
    last_name VARCHAR(80),
    email VARCHAR(80) NOT NULL,
    about_me VARCHAR(500),
    location VARCHAR(80),
    private BOOLEAN DEFAULT NULL,
    PRIMARY KEY (user_id),
    -- picture paths (aws)
    profile_pic VARCHAR(255),
    banner_pic VARCHAR(255),

    -- business stuff
    is_business BOOLEAN NOT NULL,
    address VARCHAR(80),
    city VARCHAR(80),
    state CHAR(2),
    zip_code INTEGER, 
    phone INTEGER,
    website VARCHAR(80),

    -- admin stuff
    admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE post (
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    title VARCHAR(80) NOT NULL,
    content VARCHAR(500) NOT NULL,
    file VARCHAR(255),
    post_date VARCHAR(30) NOT NULL,
    likes INTEGER NOT NULL,
    event BOOLEAN DEFAULT NULL,
    from_date VARCHAR(10),
    to_date VARCHAR(10),
    location VARCHAR(80),
    comments INTEGER NOT NULL,
    check_in BOOLEAN DEFAULT NULL,
    PRIMARY KEY (post_id)
);

CREATE TABLE user_likes (
    user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES "post"(post_id),
    like_type INTEGER NOT NULL,
    PRIMARY KEY (user_id, post_id)
);

CREATE TABLE rating (
    rating_id SERIAL NOT NULL PRIMARY KEY,
    rating SMALLINT NOT NULL,
    business_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    business_name VARCHAR(80) NOT NULL,
    post_id INTEGER NOT NULL REFERENCES post(post_id)
);

CREATE TABLE follower (
    follower_user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    followed_user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE
);

CREATE TABLE comment (
    comment_id SERIAL NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES post(post_id),
    content VARCHAR(500) NOT NULL,
    file VARCHAR(255),
    post_date VARCHAR(30) NOT NULL,
    likes INTEGER NOT NULL
);

CREATE TABLE business_items (
    business_id INTEGER NOT NULL REFERENCES "user"(user_id),
    features VARCHAR(500),
    menu_title VARCHAR(20),
    menu_file VARCHAR(255),
    PRIMARY KEY (business_id)
);
-- post has poster_id which connects to user, business, or admin
-- rating has business_id which connects to user and post_id which connects to post and then to the author