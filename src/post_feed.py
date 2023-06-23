from src.models import db, Post, User, Rating
from src.likes import likes
from src.users import users
from src.user_follow import Follows
from src.comments import comments
import uuid
import datetime
from sqlalchemy import text

class PostFeed:

    def get_all_posts(self):
        '''Returns all posts'''
        return Post.query.all()
    
    def get_posts_by_user_id(self, user_id):
        '''Returns all posts by user id order by date'''
        return Post.query.filter_by(user_id=user_id).order_by(Post.post_date.desc()).limit(15).all()
    
    def get_all_posts_ordered_by_likes(self):
        '''Returns all posts ordered by likes'''
        return Post.query.order_by(Post.likes.desc()).limit(15).all()
    
    def get_all_posts_ordered_by_date(self):
        '''Returns all posts ordered by date'''
        return Post.query.order_by(Post.post_date.desc()).limit(15).all()
    
    # WILL USE THESE FOR FILTER FUNCTIONALITY ***
    def get_all_posts_ordered_by_location(self, location):
        '''Returns all posts ordered by closest location'''
        if not location:
            return []
        location = location.split(',')
        startlat = float(location[0])
        startlng = float(location[1])
        # get 15 post ordered by closest location, post have location column that is string of "lat,lng"
        posts = db.session.execute(text(f"""
            SELECT
                p.*,
                u.*,
                distance
            FROM post p
            JOIN (
                SELECT
                    location,
                    SQRT(
                        POW(69.1 * (CAST(split_part(location, ',', 1) AS double precision) - {startlat}), 2) +
                        POW(69.1 * ({startlng} - CAST(split_part(location, ',', 2) AS double precision)) * COS(CAST(split_part(location, ',', 1) AS double precision) / 57.3), 2)
                    ) AS distance
                FROM post
            ) AS subquery
            ON p.location = subquery.location
            JOIN "user" u ON p.user_id = u.user_id
            WHERE subquery.distance < 25
            ORDER BY subquery.distance
            LIMIT 15;
        """))
        post_objects = []
        for post in posts:
            post_object = Post(post_id=post[0], user_id=post[1], title=post[2], content=post[3], file=post[4], post_date=post[5], likes=post[6], event=post[7], from_date=post[8], to_date=post[9], location=post[10], comments=post[11], check_in=post[12], user=User(user_id=post[13], username=post[14], password=post[15], first_name=post[16], last_name=post[17], email=post[18], about_me=post[19], location=post[20], private=post[21], profile_pic=post[22], banner_pic=post[23], is_business=post[24], address=post[25], city=post[26], state=post[27], zip_code=post[28], phone=post[29], website=post[30]))
            post_object.distance = post[32]
            post_objects.append(post_object)
        if not post_objects:
            return None
        return post_objects
    
    def get_all_following_posts(self, user_id):
        '''Returns all posts by users that the user is following ordered by date'''
        user = users.get_user_by_id(user_id)
        following_list = Follows.get_all_following(user_id)
        following_posts = []
        for user_id in following_list:
            posts = self.get_posts_by_user_id(user.user_id)
            following_posts += posts
            if len(following_posts) > 15:
                break
        following_posts.sort(key=lambda x: x.post_date, reverse=True)
        return following_posts
    
    def get_all_posts_by_business(self):
        '''Returns all posts where user is a business'''
        # get all posts by business ordered by date
        return Post.query.join(User).filter(User.is_business==True).order_by(Post.post_date.desc()).limit(15).all()
    
    def get_all_posts_by_event(self):
        '''Returns all posts that are events'''
        # get all posts that are events ordered by date
        return Post.query.filter(Post.event==True).order_by(Post.post_date.desc()).all()
    # ***

    def get_all_events_by_businessID(self, user_id):
        '''Returns all events by business'''
        # get all posts that are events by a particular business
        events = Post.query.filter(Post.user_id==user_id, Post.event==True).all()
        return events
    
    def get_all_posts_by_check_in(self, user_id):
        '''Returns all posts where user has checked in'''
        # get all posts where user has checked in
        # obtain post ID where all ratings are for given user ID
        # filter posts by post ID 
        post = Post.query.join(Rating).filter(Rating.post_id==Post.post_id, Rating.business_id==user_id).order_by(Post.post_date.desc()).all() 
        return post

    def get_event(self, location):
        '''Return one post that is an event ordered by from_date and location'''
        if not location:
            return []
        location = location.split(',')
        startlat = float(location[0])
        startlng = float(location[1])
        # get post ordered by closest location, post have location column that is string of "lat,lng"
        posts = db.session.execute(text(f"""
            SELECT
                p.*,
                u.*,
                distance
            FROM post p
            JOIN (
                SELECT
                    location,
                    SQRT(
                        POW(69.1 * (CAST(split_part(location, ',', 1) AS double precision) - {startlat}), 2) +
                        POW(69.1 * ({startlng} - CAST(split_part(location, ',', 2) AS double precision)) * COS(CAST(split_part(location, ',', 1) AS double precision) / 57.3), 2)
                    ) AS distance
                FROM post
            ) AS subquery
            ON p.location = subquery.location
            JOIN "user" u ON p.user_id = u.user_id
            WHERE subquery.distance < 25 AND p.event = True
            ORDER BY subquery.distance;
        """))
        date = str(datetime.datetime.now()).split(' ')[0]
        for post in posts:
            if post.from_date <= str(date) and post.to_date >= str(date):
                return post
        return None

    def get_post_by_id(self, post_id):
        '''Returns post by id'''
        return Post.query.get(post_id)
    
    def create_post(self, user_id, title, content, file, likes, event, from_date, to_date, check_in):
        '''Creates a post'''
        # create uuid for post_id
        id = uuid.uuid1()
        id = id.int
        # make the id 12 digits
        id = str(id)
        id = id[:8]
        id = int(id)
        # get current date
        date = datetime.datetime.now()
        user = users.get_user_by_id(user_id)
        if (user.location and check_in) or (user.location and event):
            location = user.location.split(',')
            startlat = float(location[0])
            startlng = float(location[1])
            posts = db.session.execute(text(f"""
                SELECT
                    u.*,
                    distance
                FROM "user" u
                JOIN (
                    SELECT
                        location,
                        SQRT(
                            POW(69.1 * (CAST(split_part(location, ',', 1) AS double precision) - {startlat}), 2) +
                            POW(69.1 * ({startlng} - CAST(split_part(location, ',', 2) AS double precision)) * COS(CAST(split_part(location, ',', 1) AS double precision) / 57.3), 2)
                        ) AS distance
                    FROM "user"
                ) AS subquery
                ON u.location = subquery.location
                WHERE subquery.distance < 25 AND u.is_business = True
                ORDER BY subquery.distance;
            """))
            for post in posts:
                location = post[7]
                break
        else:
            location = None
        post = Post(post_id=id, user_id=user_id, title=title, content=content, file=file, post_date=date, likes=likes, event=event, from_date=from_date, to_date=to_date, location=location, comments=0, check_in=check_in)
        
        db.session.add(post)
        db.session.commit()
        return post
    
    def update_post(self, post_id, title, content, file, event, from_date, to_date, check_in):
        '''Updates a post'''
        post = self.get_post_by_id(post_id)
        post.title = title
        post.content = content
        post.file = file
        post.event = event
        post.from_date = from_date
        post.to_date = to_date
        post.check_in = check_in
        db.session.commit()
        return post
    
    def search_posts(self, search):
        '''Query post titles, content, and usernames ignore case'''
        user = users.search_user(search)
        user_id = 0
        if user:
            user_id = user.user_id
        posts = Post.query.filter(Post.title.ilike(f'%{search}%') | Post.content.ilike(f'%{search}%')).all()
        user_posts = Post.query.filter(Post.user_id == user_id).all()
        all_return_posts = posts + user_posts
        # remove duplicates
        return_posts = []
        for post in all_return_posts:
            if post not in return_posts:
                return_posts.append(post)
        return return_posts

    def delete_post(self, post_id):
        '''Deletes a post'''
        post = self.get_post_by_id(post_id)
        db.session.delete(post)
        db.session.commit()
        return post
    
    def like_post(self, post_id, user_id):
        '''Likes a post'''
        # get like and post object that we need
        like = likes.get_like_by_user_id_and_post_id(user_id, post_id)
        post = self.get_post_by_id(post_id)
        # if a like already exists
        if like:
            # if the like is a dislike, remove the dislike
            if like.like_type == -1:
                post.likes += 1
                likes.update_like(user_id, post_id, 0)
            elif like.like_type == 0: # if unliked, like the post
                post.likes += 1
                likes.update_like(user_id, post_id, 1)
            else: # if this happens, the user is trying to like a post they already liked (aka inspect element)
                return
        # if a like does not exist, make a new one
        else:
            likes.create_like(user_id, post_id, 1)
            post.likes += 1
        # add and commit everything
        db.session.add(post)
        db.session.commit()

    def dislike_post(self, post_id, user_id):
        '''Dislikes a post'''
        # get the like and post object that we need
        like = likes.get_like_by_user_id_and_post_id(user_id, post_id)
        post = self.get_post_by_id(post_id)
        # if a like already exists
        if like:
            # if the like is a like, remove the like and add a dislike
            if like.like_type == 1:
                post.likes -= 2
            elif like.like_type == 0: # if unliked, dislike the post
                post.likes -= 1
            else: # if this happens, the user is trying to dislike a post they already disliked (aka inspect element)
                return
            likes.update_like(user_id, post_id, -1)
        else: # if a like does not exist, make a new one
            likes.create_like(user_id, post_id, -1)
            post.likes -= 1
        # add and commit everything
        db.session.add(post)
        db.session.commit()

    def remove_like(self, post_id, user_id):
        '''Removes a like or dislike'''
        # get the like object that we need
        like = likes.get_like_by_user_id_and_post_id(user_id, post_id)
        # if a like exists
        if like:
            post = self.get_post_by_id(post_id)
            if like.like_type == 1: # if the like is a like, remove the like
                post.likes -= 1
            elif like.like_type == -1: # if the like is a dislike, remove the dislike
                post.likes += 1
            else:
                return # if this happens, the user is trying to remove a like they don't have (aka inspect element)
            likes.update_like(user_id, post_id, 0)
        else:
            return # if this happens, the user is trying to remove a like they don't have (aka inspect element)
        # add and commit everything
        db.session.add(post)
        db.session.commit()

    def comment_on_post(self, user_id, post_id, comment, file):
        '''Comments on a post'''
        post = self.get_post_by_id(post_id)
        post.comments += 1
        comments.create_comment(post_id, user_id, comment, file)
        db.session.add(post)
        db.session.commit()

    def delete_comment(self, comment_id):
        '''Deletes a comment'''
        comment = comments.get_comment_by_id(comment_id)
        post = self.get_post_by_id(comment.post_id)
        post.comments -= 1
        comments.delete_comment(comment_id)
        db.session.add(post)
        db.session.commit()

    def clear(self):
        '''Clears all posts'''
        Post.query.delete()
        db.session.commit()

post_feed = PostFeed()