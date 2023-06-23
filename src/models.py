from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User Model
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(80), nullable=False)
    about_me = db.Column(db.String(80), nullable=True)
    location = db.Column(db.String(80), nullable=True)
    private = db.Column(db.Boolean, nullable=False)

    # picture paths
    profile_pic = db.Column(db.String(255), nullable=True)
    banner_pic = db.Column(db.String(255), nullable=True)

    # Business
    is_business = db.Column(db.Boolean, nullable=False)
    address = db.Column(db.String(80), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    state = db.Column(db.String(80), nullable=True)
    zip_code = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(80), nullable=True)
    website = db.Column(db.String(80), nullable=True)

    # admin
    admin = db.Column(db.Boolean, nullable=False)

# Post Model
class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', backref='users', lazy=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(80), nullable=False)
    file = db.Column(db.String(255), nullable=True)
    post_date = db.Column(db.DateTime, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    event = db.Column(db.Boolean, nullable=True)
    from_date = db.Column(db.String(10), nullable=True)
    to_date = db.Column(db.String(10), nullable=True)
    location = db.Column(db.String(80), nullable=True)
    comments = db.Column(db.Integer, nullable=False)
    check_in = db.Column(db.Boolean, nullable=True)

# Likes Model
class UserLikes(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, primary_key=True)
    like_type = db.Column(db.Integer, nullable=False)

# Rating Model
class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.SmallInteger, nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    business_name = db.Column(db.String(80), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)
        
    def __init__(self, rating, business_id, business_name, post_id):
        self.rating = rating
        self.business_id = business_id
        self.business_name = business_name
        self.post_id = post_id

    def __repr__(self):
        return f'{self.rating}-star rating created for {self.business_id} by {self.post_id}'
    
class Follower(db.Model):
    follower_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    followed_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)

class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', backref='comment_users', lazy=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)
    content = db.Column(db.String(80), nullable=False)
    file = db.Column(db.String(255), nullable=True)
    post_date = db.Column(db.DateTime, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

class BusinessItems(db.Model):
    business_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True, nullable=False)
    business = db.relationship('User', backref='business_items', lazy=True)
    features = db.Column(db.String(255), nullable=True)
    menu_title = db.Column(db.String(20), nullable=True)
    menu_file = db.Column(db.String(255), nullable=True)