import pathlib
from flask import Flask, flash, abort, render_template, redirect, request, session, g, url_for, send_from_directory
import requests
from src.post_feed import post_feed
from src.users import users
from src.likes import likes
from src.rating import rating
from src.user_follow import Follows
from src.models import db, User, Rating
from src.comments import comments
from src.business_items import business_items
from dotenv import load_dotenv
import os
import re
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from pip._vendor import cachecontrol
import boto3
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import uuid


app = Flask(__name__)

# Database Connection
load_dotenv()

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] \
    = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False # set to True to see SQL queries
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max upload size

db.init_app(app)

# vars
app.secret_key = os.getenv('SECRET_KEY')
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
bcrypt = Bcrypt(app)

# Google Auth
url = os.getenv('URL')
GOOGLE_CLIENT_ID = '402126507734-2knh1agkn688s2atb55a5oeu062j89f8.apps.googleusercontent.com'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # comment out for production ***
client_secret_file = os.path.join(pathlib.Path(__file__).parent, 'client_secret.json')
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secret_file,
    scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid'],
    redirect_uri=f'{url}/callback'
)

# AWS S3 Connection
aws_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket_name = os.getenv('BUCKET_NAME')
s3 = boto3.resource('s3',
aws_access_key_id=aws_id,
aws_secret_access_key=aws_secret)
bucket_name = bucket_name


# Check if user is logged in
def logged_in():
    '''Checks if user is logged in'''
    if 'user_id' in session:
        return True
    else:
        return False


@app.before_request
def before_request():
    '''Checks if user is logged in'''
    # comments.clear()
    # likes.clear()
    # rating.clear()
    # Follows.clear()
    # post_feed.clear()
    # users.clear()
    g.user = None
    if 'user_id' in session:
        user = users.get_user_by_id(session['user_id'])
        if user == None:
            session.pop('user_id', None)
        else:
            g.user = user

# update location and pass in pos from ajax
@app.route('/update_location', methods=['POST'])
def update_location():
    if not g.user:
        return redirect(url_for('login'))
    request_data = request.get_json()
    lat = round(request_data['lat'], 5)
    lng = round(request_data['lng'], 5)
    users.update_location(g.user.user_id, lat, lng)
    return "nothing"


@app.route('/')
def index():
    if not g.user:
        return render_template('index.html', logged_in=False, home="active")
    return render_template('index.html', logged_in=True, home="active", posts=post_feed.get_all_posts_ordered_by_likes(), likes=likes.get_all_likes(), ratings=rating.get_all_ratings(), event=post_feed.get_event(g.user.location))

@app.route('/feed')
def feed():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('index.html', logged_in=True, feed="active", posts=post_feed.get_all_posts_ordered_by_date(), likes=likes.get_all_likes(), ratings=rating.get_all_ratings())

# filter feed
@app.route('/feed/filter', methods=['POST'])
def filter_feed():
    filter = request.form.get('filter')
    if not filter:
        return redirect(url_for('feed'))
    if not g.user:
        return redirect(url_for('login'))
    if filter == 'location':
        posts = post_feed.get_all_posts_ordered_by_location(g.user.location)
    elif filter == 'follow':
        posts = post_feed.get_all_following_posts(g.user.user_id)
    elif filter == 'venues':
        posts = post_feed.get_all_posts_by_business()
    elif filter == 'events':
        posts = post_feed.get_all_posts_by_event()
    else:
        return redirect(url_for('feed'))
    mylikes = likes.get_all_likes()
    ratings = rating.get_all_ratings()
    return render_template('feed.html', posts=posts, likes=mylikes, ratings=ratings, selected=filter)

# account page
@app.route('/account')
def account():
    star = 0
    if not g.user:
        return redirect(url_for('login'))
    if g.user.is_business:
        star = rating.get_rating_average(g.user.user_id)
    followers_num = Follows.get_followers_num(g.user, g.user.user_id)
    return render_template('account.html', account="active", posts=post_feed.get_posts_by_user_id(g.user.user_id), likes=likes.get_all_likes(), ratings = rating.get_all_ratings(), rating=star, followers_num=followers_num)



#followers page
@app.route('/account/followers')
def account_followers():
    followers = Follows.get_all_followers(g.user.user_id)
    followerBool = True
    followers_num = Follows.get_followers_num(g.user, g.user.user_id)
    star = 0
    if g.user.is_business:
        star = rating.get_rating_average(g.user.user_id)
    return render_template('account.html',followers=followers,followerBool=followerBool,followers_num=followers_num,rating=star)


@app.route('/account/edit', methods=['GET', 'POST'])
def edit_account():
    if request.method == 'GET':
        if not g.user:
            return redirect(url_for('login'))
        if g.user.is_business:
            return render_template('settings_business.html', account="active")
        return render_template('settings.html', account="active")
    else:
        if not g.user:
            return redirect(url_for('login'))
        
        if g.user.is_business:    
            user_id = session['user_id']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            about_me = request.form['about_me']
            profile_pic = request.files['profile_pic']
            banner_pic = request.files['banner_pic']
            private = request.form.get('private')
            city = request.form['city']
            address = request.form['address']
            state = request.form['state']
            zip_code = request.form['zip_code']
        else:
            user_id = session['user_id']
            username = request.form['username']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            about_me = request.form['about_me']
            profile_pic = request.files['profile_pic']
            banner_pic = request.files['banner_pic']
            private = request.form.get('private')

        # upload files
        try:
            # set old profile pic paths
            profile_pic_path = g.user.profile_pic
            banner_pic_path = g.user.banner_pic
            if profile_pic:
                # check if file is an image
                if not profile_pic.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return render_template('settings.html', message='Profile picture must be a .jpg, .jpeg, or .png file.')
                new_profile_filename = f'{uuid.uuid4()}_{secure_filename(profile_pic.filename)}'.replace(' ', '_')

                # remove old profile pic from s3
                user = users.get_user_by_id(user_id)
                if user.profile_pic != None:
                    print(g.user.profile_pic.split('/')[-1])
                    s3.Object(bucket_name, g.user.profile_pic.split('/')[-1]).delete()

                # upload new profile pic to s3
                s3.Bucket(bucket_name).upload_fileobj(
                    profile_pic,
                    new_profile_filename
                )

                # add filepath to database
                profile_pic_path = f'https://barhive.s3.amazonaws.com/{new_profile_filename}'
            if banner_pic:
                # check if file is a picture
                if not banner_pic.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return render_template('settings.html', message='Banner picture must be a .jpg, .jpeg, or .png file.')
                new_banner_filename = f'{uuid.uuid4()}_{secure_filename(banner_pic.filename)}'.replace(' ', '_')

                # remove old banner pic from s3
                user = users.get_user_by_id(user_id)
                if user.banner_pic != None:
                    print(g.user.banner_pic.split('/')[-1])
                    s3.Object(bucket_name, g.user.banner_pic.split('/')[-1]).delete()

                # upload new banner pic to s3
                s3.Bucket(bucket_name).upload_fileobj(
                    banner_pic,
                    new_banner_filename
                )

                # add filepath to database
                banner_pic_path = f'https://barhive.s3.amazonaws.com/{new_banner_filename}'
        except Exception as e:
            print(f"Error uploading files to s3: " + str(e))

    if g.user.is_business:
        # address handling
        if city == "":
            city = None
        if address == "":
            address = None
        if state == "":
            state = None
        if zip_code == "":
            zip_code = None
        if password != "":
            message = ""
            unsaved_user = User(user_id=user_id, username=username, password=password, email=email, private=private, city=city, address=address, state=state, zip_code=zip_code)
            if password != confirm_password:
                message = 'Passwords do not match.'
                return render_template('settings.html', user=unsaved_user, message=message, logged_in=logged_in(), account="active")
            if len(password) < 6:
                message = 'Password must be at least 6 characters.'
                return render_template('settings.html', user=unsaved_user, message=message, logged_in=logged_in(), account="active")
            password = bcrypt.generate_password_hash(password).decode()
        else:
            password = g.user.password
        users.update_user(user_id=user_id, username=username, password=password, email=email, about_me=about_me, private=private, profile_pic=profile_pic_path, banner_pic=banner_pic_path, is_business=True, city=city, address=address, state=state, zip_code=zip_code)
        return redirect(url_for('account'))
    try:
        # needs more error handling
        if password != "":
            message = ""
            unsaved_user = User(user_id=user_id, username=username, password=password, first_name=first_name, last_name=last_name, email=email, about_me=about_me, private=private)
            if password != confirm_password:
                message = 'Passwords do not match.'
                return render_template('settings.html', user=unsaved_user, message=message, logged_in=logged_in(), account="active")
            if len(password) < 6:
                message = 'Password must be at least 6 characters.'
                return render_template('settings.html', user=unsaved_user, message=message, logged_in=logged_in(), account="active")
            password = bcrypt.generate_password_hash(password).decode()
        else:
            password = g.user.password
        print(profile_pic_path)
        users.update_user(user_id=user_id, username=username, password=password, first_name=first_name, last_name=last_name, email=email, about_me=about_me, private=private, profile_pic=profile_pic_path, banner_pic=banner_pic_path)
        return redirect(url_for('account'))
    except Exception as e: 
        print(e)
        error_message = str(e)
        return render_template('error.html', error_message=error_message)
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('index'))
    info = {}
    if request.method == 'POST':
        session.pop('user_id',None)
        email = request.form['email']
        password = request.form['password']
        if password is None:
            abort(400)
        user = users.get_user_by_email(email)
        if user and user.password is not None and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            return redirect(url_for('account'))
        else:
            message = f"Username or password incorrect."
            return render_template('login.html', message=message, logged_in=logged_in(), login="active", info=info)
    return render_template('login.html', logged_in=logged_in(), login="active", info=info)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('index'))
    info = {}
    if request.method == 'POST':
        global logged_in
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        info = {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password}
        
        # error handling
        if username == "" or email == "" or password == "" or confirm_password == "":
            message = 'All fields are required.'
            return render_template('register.html', message=message, logged_in=logged_in(), register="active", info=info)
        if not (re.fullmatch(regex, email)):
            message = 'Email is not valid.'
            return render_template('register.html', message=message, logged_in=logged_in(), register="active", info=info)
        if password != confirm_password:
            message = 'Passwords do not match.'
            return render_template('register.html', message=message, logged_in=logged_in(), register="active", info=info)
        if len(password) < 6:
            message = 'Password must be at least 6 characters.'
            return render_template('register.html', message=message, logged_in=logged_in(), register="active", info=info)
        existing_user = users.get_user_by_username(username)
        if existing_user:
            message = 'Username already exists.'
            return render_template('register.html', message=message, logged_in=logged_in(), register="active", info=info)
        existing_email = users.get_user_by_email(email)
        if existing_email:
            message = 'email'
            return render_template('register.html', message=message, logged_in=logged_in(), register="active", info=info)
        
        hashed_password = bcrypt.generate_password_hash(password).decode()
        new_user = users.create_user(username, email, hashed_password)
        session['user_id'] = new_user.user_id

        return redirect(url_for('account'))
    
    return render_template('register.html', logged_in=logged_in(), register="active", info=info)


# create post
@app.route('/create', methods=['GET', 'POST'])
def create():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('create.html', business=users.get_business_by_location(g.user.location))
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        if len(title) > 80 or len(content) > 500:
            abort(400)
        file = request.files['file']
        check_in = bool(request.form.get('rating'))
        if check_in:
            business_id = request.form.get('business')
            stars = request.form.get('rating')
        if g.user.is_business:
            event = request.form.get('event')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            if event == "1":
                event = True
            else:
                event = False
            if event:
                if from_date != None:
                    from_date = from_date.replace(" ", "")
                if to_date != None:
                    to_date = to_date.replace(" ", "")
            else:
                from_date = None
                to_date = None
        else:
            event = None
            from_date = None
            to_date = None
        if title == "":
            abort(400)
        post_path = None
        if file:
            try:
                # make sure file is an image
                if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return render_template('settings.html', message='Image must be a .jpg, .jpeg, or .png file.')
                new_post_filename = f'{uuid.uuid4()}_{secure_filename(file.filename)}'.replace(' ', '_')

                # upload file to s3
                s3.Bucket(bucket_name).upload_fileobj(
                    file,
                    new_post_filename
                )

                # add filepath to database
                post_path = f'https://barhive.s3.amazonaws.com/{new_post_filename}'
            except Exception as e:
                print(f"Error uploading files to s3: " + str(e))

        # get user id
        user_id = session['user_id']
        post = post_feed.create_post(user_id, title, content, post_path, 0, event, from_date, to_date, check_in)
        if check_in: 
            rating.create_rating(stars, business_id, post.post_id)
        return redirect('/feed')


# delete post
@app.get('/feed/delete/<post_id>')
def delete_post(post_id):
    if not g.user:
        return redirect(url_for('login'))
    if not g.user.admin:
        if g.user.user_id != post_feed.get_post_by_id(post_id).user_id:
            return redirect('/error')
    post = post_feed.get_post_by_id(post_id)
    # delete all comments with post id
    post_comments = comments.get_comments_by_post_id(post_id)
    for comment in post_comments:
        # if comment has a file, delete it
        if comment.file:
            s3.Object(bucket_name, comment.file.split('/')[-1]).delete()
        comments.delete_comment(comment.comment_id)
        likes.delete_likes_by_post_id(comment.comment_id)
    if post.file:
        # delete file from s3
        post = post_feed.get_post_by_id(post_id)
        s3.Object(bucket_name, post.file.split('/')[-1]).delete()
    rating.delete_rating_by_post_id(post_id)
    likes.delete_likes_by_post_id(post_id)
    post_feed.delete_post(post_id)
    return redirect('/feed')

# delete post
@app.get('/account/post/<post_id>/delete')
def delete_post_account(post_id):
    if not g.user:
        return redirect(url_for('login'))
    if g.user.user_id != post_feed.get_post_by_id(post_id).user_id:
        return redirect('/error')
    post = post_feed.get_post_by_id(post_id)
    # delete all comments with post id
    post_comments = comments.get_comments_by_post_id(post_id)
    for comment in post_comments:
        # if comment has a file, delete it
        if comment.file:
            s3.Object(bucket_name, comment.file.split('/')[-1]).delete()
        comments.delete_comment(comment.comment_id)
        likes.delete_likes_by_post_id(comment.comment_id)
    if post.file:
        # delete file from s3
        post = post_feed.get_post_by_id(post_id)
        s3.Object(bucket_name, post.file.split('/')[-1]).delete()
    rating.delete_rating_by_post_id(post_id)
    likes.delete_likes_by_post_id(post_id)
    post_feed.delete_post(post_id)
    return redirect('/account')


# like post
@app.get('/feed/like/<int:post_id>')
def like_post(post_id):
    if g.user:
        user_id = session['user_id']
    else:
        return redirect('/error')
    post_feed.like_post(post_id, user_id)
    return "nothing"

# dislike post
@app.get('/feed/dislike/<int:post_id>')
def dislike_post(post_id):
    if g.user:
        user_id = session['user_id']
    else:
        return redirect('/error')
    post_feed.dislike_post(post_id, user_id)
    return "nothing"

# remove like or dislike
@app.get('/feed/remove_like/<int:post_id>')
def remove_like(post_id):
    if g.user:
        user_id = session['user_id']
    else:
        return redirect('/error')
    post_feed.remove_like(post_id, user_id)
    return "nothing"

# edit post
@app.route('/feed/edit/<post_id>', methods=['GET', 'POST'])
def edit(post_id):
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'GET':
        if g.user.user_id != post_feed.get_post_by_id(post_id).user_id:
            return redirect('/error')
        return render_template('edit.html', post=post_feed.get_post_by_id(post_id), business=users.get_business_by_location(g.user.location), rating=rating.get_rating_by_post_id(post_id))
    else:
        if g.user.user_id != post_feed.get_post_by_id(post_id).user_id:
            return redirect('/error')
        title = request.form.get('title')
        content = request.form.get('content')
        if len(title) > 80 or len(content) > 500:
            abort(400)
        file = request.files['file']
        check_in = bool(request.form.get('rating'))
        if check_in:
            business_id = request.form.get('business')
            stars = request.form.get('rating')
        if g.user.is_business:
            event = request.form.get('event')
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            if event == "1":
                event = True
            else:
                event = False
            if event:
                if from_date != None:
                    from_date = from_date.replace(" ", "")
                if to_date != None:
                    to_date = to_date.replace(" ", "")
            else:
                from_date = None
                to_date = None
        else:
            event = None
            from_date = None
            to_date = None
        file_path = post_feed.get_post_by_id(post_id).file or None
        if file:
            try:
                if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return render_template('settings.html', message='Banner picture must be a .jpg, .jpeg, or .png file.')
                new_filename = f'{uuid.uuid4()}_{secure_filename(file.filename)}'.replace(' ', '_')

                # remove old banner pic from s3
                post = post_feed.get_post_by_id(post_id)
                if post.file != None:
                    s3.Object(bucket_name, post.file.split('/')[-1]).delete()

                s3.Bucket(bucket_name).upload_fileobj(
                    file,
                    new_filename
                )

                # add filepath to database
                file_path = f'https://barhive.s3.amazonaws.com/{new_filename}'
            except Exception as e:
                print(f"Error uploading files to s3: " + str(e))

        post_feed.update_post(post_id, title, content, file=file_path, event=event, from_date=from_date, to_date=to_date, check_in=check_in)
        if check_in: 
            existing_rating = rating.get_rate_object_by_post_id(post_id)
            if existing_rating:
                rating.update_rating(existing_rating.rating_id, stars)
            else:
                rating.update_rating(stars, post_id)
        return redirect('/feed')


#  view post
@app.get('/feed/<post_id>')
def view_post(post_id):
    if not g.user:
        return redirect(url_for('login'))
    post = post_feed.get_post_by_id(post_id)
    if post:
        stars = rating.get_rating_by_post_id(post_id)
        return render_template('view_post.html', post=post, likes=likes.get_all_likes(), comments=comments.get_comments_by_post_id(post_id), rating=stars, ratings=rating.get_all_ratings(), users=users.get_all_users())

    return redirect('/error')

# view user
@app.get('/user/<user_id>')
def view_user(user_id):
    if not g.user:
        return redirect(url_for('login'))
    if g.user:
        if int(g.user.user_id) == int(user_id):
            return redirect('/account')
    user = users.get_user_by_id(user_id)
    if user:
        followers_num = Follows.get_followers_num(user, user_id)
        is_Following=Follows.is_Foo_Following_Bar(g.user.user_id,user_id)
        star = rating.get_rating_average(user.user_id)
        return render_template('account.html', user=user, followers_num=followers_num, user_id=user_id, is_Following=is_Following, rating=star, posts=post_feed.get_posts_by_user_id(user_id), likes=likes.get_all_likes())
    return redirect('/error')

#view a other users followers
@app.get('/user/<user_id>/followers')
def view_user_followers(user_id):
    user = users.get_user_by_id(user_id)
    followers = Follows.get_all_followers(user_id)
    followerBool = True
    star = rating.get_rating_average(user.user_id)
    is_Following=Follows.is_Foo_Following_Bar(g.user.user_id,user_id)
    followers_num = Follows.get_followers_num(user, user_id)
    return render_template('account.html',user=user,followers=followers,followerBool=followerBool,followers_num=followers_num,is_Following=is_Following,rating=star)

#follow method
@app.route('/follow/<user_id>', methods=['POST'])
def follow(user_id):
    #is_Following = True
    Follows.foo_followed_bar(g.user,g.user.user_id,user_id)
    is_Following = True
    return redirect(url_for('view_user',user_id=user_id,is_Following=is_Following))

#unfollow method
@app.route('/unfollow/<user_id>', methods=['POST'])
def unfollow(user_id):
    #is_Following = False
    Follows.foo_unfollowed_bar(g.user.user_id,user_id)
    is_Following = False
    return redirect(url_for('view_user',user_id=user_id,is_Following=is_Following))

# business page
@app.route('/business/register', methods=['GET', 'POST'])
def business():
    info = {}
    if request.method == 'POST':
        global logged_in
        business_name = request.form['business_name']
        business_email = request.form['business_email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        info = {'business_name': business_name, 'business_email': business_email, 'password': password, 'confirm_password': confirm_password}
        
        if business_name == "" or business_email == "" or password == "" or confirm_password == "":
            message = 'All fields are required.'
            return render_template('business_register.html', message=message, logged_in=logged_in(), register="active", info=info)
        if not (re.fullmatch(regex, business_email)):
            message = 'Email is not valid.'
            return render_template('business_register.html', message=message, logged_in=logged_in(), register="active", info=info)
        if password != confirm_password:
            message = 'Passwords do not match.'
            return render_template('business_register.html', message=message, logged_in=logged_in(), register="active", info=info)
        if len(password) < 6:
            message = 'Password must be at least 6 characters.'
            return render_template('business_register.html', message=message, logged_in=logged_in(), register="active", info=info)
        
        existing_user = users.get_user_by_username(business_name)
        if existing_user:
            message = 'Username already exists.'
            return render_template('business_register.html', message=message, logged_in=logged_in(), register="active", info=info)
        
        existing_email = users.get_user_by_email(business_email)
        if existing_email:
            message = 'email'
            return render_template('business_register.html', message=message, logged_in=logged_in(), register="active", info=info)
        
        hashed_password = bcrypt.generate_password_hash(password).decode()
        new_user = users.create_user(username=business_name, email=business_email, password=hashed_password, is_business=True)
        session['user_id'] = new_user.user_id
        business_items.create_business_items(new_user.user_id)

        return redirect(url_for('account'))
    
    return render_template('business_register.html', logged_in=logged_in(), register="active", info=info)

# search page
@app.get('/search')
def search():
    if not g.user:
        return redirect(url_for('login'))
    query = request.args.get('query')
    if query:
        posts = post_feed.search_posts(query)
        return render_template('search.html', posts=posts, query=query)
    return redirect('/error')


# comment on post
@app.route('/feed/<post_id>/comment', methods=['POST'])
def comment(post_id):
    comment = request.form.get('content')
    file = request.files['file']
    file_path = None
    if file:
            try:
                if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return render_template('settings.html', message='Banner picture must be a .jpg, .jpeg, or .png file.')
                new_filename = f'{uuid.uuid4()}_{secure_filename(file.filename)}'

                s3.Bucket(bucket_name).upload_fileobj(
                    file,
                    new_filename
                )

                # add filepath to database
                file_path = f'https://barhive.s3.amazonaws.com/{new_filename}'
            except Exception as e:
                print(f"Error uploading files to s3: " + str(e))

    post_feed.comment_on_post(user_id=g.user.user_id, post_id=post_id, comment=comment, file=file_path)
    return redirect(url_for('view_post', post_id=post_id))

# edit comment
@app.route('/feed/<post_id>/comment/<comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(post_id, comment_id):
    comment = comments.get_comment_by_id(comment_id)
    if request.method == 'POST':
        comment_data = request.form.get('content')
        file = request.files['file']
        file_path = comment.file or None
        if file:
            try:
                if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return render_template('edit_comment.html', message='Banner picture must be a .jpg, .jpeg, or .png file.')
                new_filename = f'{uuid.uuid4()}_{secure_filename(file.filename)}'

                # remove old banner pic from s3
                comment = comments.get_comment_by_id(comment_id)
                if comment.file != None:
                    s3.Object(bucket_name, comment.file.split('/')[-1]).delete()

                s3.Bucket(bucket_name).upload_fileobj(
                    file,
                    new_filename
                )

                # add filepath to database
                file_path = f'https://barhive.s3.amazonaws.com/{new_filename}'
            except Exception as e:
                print(f"Error uploading files to s3: " + str(e))

        file = file_path
        comments.update_comment(comment_id, comment_data, file)
        return redirect(url_for('view_post', post_id=post_id))
    return render_template('edit_comment.html', comment=comment, post_id=post_id)

# delete comment
@app.route('/feed/<post_id>/comment/<comment_id>/delete')
def delete_comment(post_id, comment_id):
    comment = comments.get_comment_by_id(comment_id)
    if comment.file:
        # delete file from s3
        s3.Object(bucket_name, comment.file.split('/')[-1]).delete()
    post_feed.delete_comment(comment_id)
    return redirect(url_for('view_post', post_id=post_id))

# like post
@app.get('/feed/comment/like/<int:comment_id>')
def like_comment(comment_id):
    if g.user:
        user_id = session['user_id']
    else:
        return redirect('/error')
    comments.like_post(comment_id, user_id)
    return "nothing"

# dislike post
@app.get('/feed/comment/dislike/<int:comment_id>')
def dislike_comment(comment_id):
    if g.user:
        user_id = session['user_id']
    else:
        return redirect('/error')
    comments.dislike_post(comment_id, user_id)
    return "nothing"

# remove like or dislike
@app.get('/feed/comment/remove_like/<int:comment_id>')
def remove_comment_like(comment_id):
    if g.user:
        user_id = session['user_id']
    else:
        return redirect('/error')
    comments.remove_like(comment_id, user_id)
    return "nothing"


# error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', logged_in=logged_in(), e=e), 404


# ********** GOOGLE LOGIN **********
@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    
    username = id_info.get("name")
    if '(' and ')' in username:
        usernames = username.split(" ")
        username = usernames[len(usernames) - 1].replace("(", "")
        username = username.replace(")", "")
    
    # check if user exists
    existing_user = users.get_user_by_email(id_info.get("email"))
    if existing_user:
        session['user_id'] = existing_user.user_id
        return redirect(url_for('account'))
    else:
        email = id_info.get("email")
        new_user = users.create_user(username, email, None)
        session['user_id'] = new_user.user_id

    return redirect(url_for('account'))

@app.route('/googlelogin')
def googlelogin():
    try:
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        return redirect(authorization_url)
    except Exception as e:
        #redirect to error page
        return redirect('/error')
# ********** GOOGLE LOGIN **********

@app.get('/user/<user_id>/features')
def view_business_features(user_id):
    user = users.get_user_by_id(user_id)
    business_stuff = business_items.get_business_items_by_user_id(user_id)
    if user:
        star = rating.get_rating_average(user_id)
    return render_template('features.html', rating=star, user=user, user_id=user_id, features=business_stuff.features)


@app.route('/user/<user_id>/events')
def view_business_events(user_id):
    user = users.get_user_by_id(user_id)
    events = post_feed.get_all_events_by_businessID(user_id)
    if user:
        star = rating.get_rating_average(user_id)
    return render_template('events.html', rating=star, user=user, user_id=user_id, events=events)


@app.route('/user/<user_id>/reviews')
def view_business_reviews(user_id):
    user = users.get_user_by_id(user_id)
    reviews = post_feed.get_all_posts_by_check_in(user_id)
    if user:
        star = rating.get_rating_average(user_id)
    return render_template('reviews.html', rating=star, user=user, user_id=user_id, reviews=reviews, ratings=rating.get_all_ratings())


@app.route('/user/<user_id>/menu')
def view_business_menu(user_id):
    user = users.get_user_by_id(user_id)
    menu_title = business_items.get_menu_title(user_id)
    menu = business_items.get_menu(user_id)
    if user:
        star = rating.get_rating_average(user_id)
    return render_template('menu.html', rating=star, user=user, user_id=user_id, menu_title=menu_title, menu=menu)


# delete user
@app.route('/account/<int:id>/delete')
def delete(id):
    users.delete_user(id)
    session.clear()
    return redirect('/')
