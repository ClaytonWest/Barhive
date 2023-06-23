from src.models import db, Follower, User

class Follows:

    #just pay close attention to which user is following which
    def foo_followed_bar(self,follower_user_id,followed_user_id):
        #need to change to only allow one!
        if Follower.query.filter_by(followed_user_id=followed_user_id,follower_user_id=follower_user_id).first():
            return 99
        else:
            follower = Follower(follower_user_id=follower_user_id,followed_user_id=followed_user_id)
            db.session.add(follower)
            db.session.commit()
            return 99
    
    def foo_unfollowed_bar(follower_user_id,followed_user_id):
        #use returns for JS? or change them?
        #also could I just do a filter and then a .delete()?
        if Follower.query.filter_by(followed_user_id=followed_user_id,follower_user_id=follower_user_id).first():
            #follower = Follower(follower_user_id=follower_user_id,followed_user_id=followed_user_id)
            follower = Follower.query.filter_by(follower_user_id=follower_user_id,followed_user_id=followed_user_id,).first()
            db.session.delete(follower)
            db.session.commit()
            return -99
        else:
            return -99
    
    def is_Foo_Following_Bar(follower_user_id,followed_user_id):
        if Follower.query.filter_by(followed_user_id=followed_user_id,follower_user_id=follower_user_id).first():
            return True
        else:
            return False
    
    def get_all_followers(self):
        follow_list = User.query.join(Follower, User.user_id==Follower.follower_user_id).add_columns(User.user_id,User.username,User.profile_pic).filter_by(followed_user_id=self).all()
        return follow_list

    def get_all_following(self):
        following_list = User.query.join(Follower, User.user_id==Follower.follower_user_id).add_columns(User.user_id).filter_by(follower_user_id=self).all()
        return following_list
    def get_followers_num(self,followed_user_id):
        
        num_followers = Follower.query.filter_by(followed_user_id=followed_user_id).count()
        return num_followers
    
    def get_user_by_follower_id(self,follower_user_id):
        return User.query.get(follower_user_id)
    
    def clear():
        Follower.query.delete()
        db.session.commit()
    
follows = Follows()