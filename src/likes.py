from src.models import db, UserLikes

class Likes:

    def get_all_likes(self):
        '''Returns all likes'''
        return UserLikes.query.all()
    
    def get_like_by_post_id(self, post_id):
        '''Returns like by id'''
        return UserLikes.query.filter_by(post_id=post_id).all()
    
    def get_like_by_user_id_and_post_id(self, user_id, post_id):
        '''Returns like by id'''
        return UserLikes.query.filter_by(user_id=user_id, post_id=post_id).first()
    
    def create_like(self, user_id, post_id, like_type):
        '''Creates a like'''
        like = UserLikes(user_id=user_id, post_id=post_id, like_type=like_type)
        db.session.add(like)
        db.session.commit()
        return like
    
    def update_like(self, user_id, post_id, like_type):
        '''Updates a like'''
        like = self.get_like_by_user_id_and_post_id(user_id, post_id)
        like.like_type = like_type
        db.session.commit()
        return like
    
    def delete_likes_by_post_id(self, post_id):
        '''Deletes likes by post id'''
        likes = self.get_like_by_post_id(post_id)
        for like in likes:
            db.session.delete(like)
        db.session.commit()
    
    def clear(self):
        '''Clears all likes'''
        UserLikes.query.delete()
        db.session.commit()
    
likes = Likes()