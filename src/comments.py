from src.models import db, Comment
from src.users import users
from src.likes import likes
import datetime

class CommentFeed:
    
    def get_all_comments(self):
        '''Returns all comments'''
        return Comment.query.all()
    
    def get_comments_by_post_id(self, post_id):
        '''Returns all comments by post id, order by likes'''
        return Comment.query.filter_by(post_id=post_id).order_by(Comment.likes.desc()).all()
    
    def get_comment_by_id(self, comment_id):
        '''Returns comment by id'''
        return Comment.query.get(comment_id)
    
    def create_comment(self, post_id, user_id, content, file):
        '''Creates a comment'''
        # get current date
        date = datetime.datetime.now()
        comment = Comment(post_id=post_id, user_id=user_id, content=content, file=file, post_date=date, likes=0)
        db.session.add(comment)
        db.session.commit()
        return comment
    
    def update_comment(self, comment_id, content, file):
        '''Updates a comment'''
        comment = self.get_comment_by_id(comment_id)
        comment.content = content
        comment.file = file
        db.session.commit()
        return comment
    
    def delete_comment(self, comment_id):
        '''Deletes a comment'''
        comment = self.get_comment_by_id(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return comment
    
    def search_comments(self, search):
        '''Query comment content and usernames ignore case'''
        user = users.search_user(search)
        user_id = 0
        if user:
            user_id = user.user_id
        return Comment.query.filter((Comment.content.ilike('%' + search + '%')) | (Comment.user_id == user_id)).all()
    
    def like_post(self, comment_id, user_id):
        '''Likes a post'''
        # get like and post object that we need
        like = likes.get_like_by_user_id_and_post_id(user_id, comment_id)
        comment = self.get_comment_by_id(comment_id)
        # if a like already exists
        if like:
            # if the like is a dislike, remove the dislike
            if like.like_type == -1:
                comment.likes += 1
                likes.update_like(user_id, comment_id, 0)
            elif like.like_type == 0: # if unliked, like the post
                comment.likes += 1
                likes.update_like(user_id, comment_id, 1)
            else: # if this happens, the user is trying to like a post they already liked (aka inspect element)
                return
        # if a like does not exist, make a new one
        else:
            likes.create_like(user_id, comment_id, 1)
            comment.likes += 1
        # add and commit everything
        db.session.add(comment)
        db.session.commit()

    def dislike_post(self, comment_id, user_id):
        '''Dislikes a post'''
        # get the like and post object that we need
        like = likes.get_like_by_user_id_and_post_id(user_id, comment_id)
        comment = self.get_comment_by_id(comment_id)
        # if a like already exists
        if like:
            # if the like is a like, remove the like and add a dislike
            if like.like_type == 1:
                comment.likes -= 2
            elif like.like_type == 0: # if unliked, dislike the post
                comment.likes -= 1
            else: # if this happens, the user is trying to dislike a post they already disliked (aka inspect element)
                return
            likes.update_like(user_id, comment_id, -1)
        else: # if a like does not exist, make a new one
            likes.create_like(user_id, comment_id, -1)
            comment.likes -= 1
        # add and commit everything
        db.session.add(comment)
        db.session.commit()

    def remove_like(self, comment_id, user_id):
        '''Removes a like or dislike'''
        # get the like object that we need
        like = likes.get_like_by_user_id_and_post_id(user_id, comment_id)
        # if a like exists
        if like:
            comment = self.get_comment_by_id(comment_id)
            if like.like_type == 1: # if the like is a like, remove the like
                comment.likes -= 1
            elif like.like_type == -1: # if the like is a dislike, remove the dislike
                comment.likes += 1
            else:
                return # if this happens, the user is trying to remove a like they don't have (aka inspect element)
            likes.update_like(user_id, comment_id, 0)
        else:
            return # if this happens, the user is trying to remove a like they don't have (aka inspect element)
        # add and commit everything
        db.session.add(comment)
        db.session.commit()

    def clear(self):
        '''Clears all comments'''
        comments = Comment.query.all()
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()
    
comments = CommentFeed()