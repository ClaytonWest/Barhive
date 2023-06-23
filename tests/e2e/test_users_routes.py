from app import app, bcrypt,db, users
from src.models import *
from src.users import *
from src.user_follow import *
from src.post_feed import *
import datetime
import uuid


def test_register(test_client):
    # Send a POST request to register a new user
    response = test_client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword',
        'confirm-password': 'testpassword'
    })

    # Check that the response redirects to the account page
    assert response.status_code == 302
    assert response.location.endswith('/account')

    # Check that the user was created in the database
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'testuser@example.com'


def test_create_post(test_client):
    # create user
    users = Users()
    posts = PostFeed()
    user = users.create_user(username='testuser', email='testuser@test.com', password='password', is_business=False)
    user_username = 'testuser'
    assert user.username==user_username
    
    # create post
    post_title = 'Test Post Title'
    post_content = 'Test post content'
    post_file = 'test_file.txt'
    post_likes = 0
    post_event = False
    post_from_date = '2023-05-10'
    post_to_date = '2023-05-11'
    post_check_in = False
    
    post = posts.create_post(user_id=user.user_id, title=post_title, content=post_content, file=post_file, likes=post_likes, event=post_event, from_date=post_from_date, to_date=post_to_date, check_in=post_check_in)
    
    assert post.title == post_title
    assert post.content == post_content
    assert post.file == post_file
    assert post.likes == post_likes
    assert post.event == post_event
    assert post.from_date == post_from_date
    assert post.to_date == post_to_date
    assert post.check_in == post_check_in