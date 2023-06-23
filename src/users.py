from src.models import db, User
import uuid
from sqlalchemy import text


class Users:

    def get_all_users(self):
        '''Returns all users'''
        return User.query.all()
    
    def get_all_businesses(self):
        '''Returns all businesses'''
        return User.query.filter_by(is_business=True).all()
    
    def get_user_by_id(self, user_id):
        '''Returns user by id'''
        return User.query.get(user_id)
    
    def get_user_by_username(self, username):
        '''Returns user by username'''
        return User.query.filter_by(username=username).first()
    
    def get_user_by_email(self, email):
        '''Returns user by email'''
        return User.query.filter_by(email=email).first()
    
    def get_business_by_location(self, location):
        '''Returns business by location'''
        if not location:
            return []
        location = location.split(',')
        startlat = float(location[0])
        startlng = float(location[1])
        # get 15 post ordered by closest location, post have location column that is string of "lat,lng"
        users = db.session.execute(text(f"""
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
            WHERE subquery.distance < 25 AND u.is_business = true
            ORDER BY subquery.distance
            LIMIT 1;
        """))
        user_object = None
        for user in users:
            print(user)
            user_object = User(user_id=user[0], username=user[1], password=user[2], first_name=user[3], last_name=user[4], email=user[5], about_me=user[6], location=user[7], private=user[8], profile_pic=user[9], banner_pic=user[10], is_business=user[11], address=user[12], city=user[13], state=user[14], zip_code=user[15], phone=user[16], website=user[17])
            user_object.distance = user[18]
        if not user_object:
            return None
        return user_object
    
    def create_user(self, username, email, password, is_business=False):
        '''Creates a user'''
        email = email.lower()
        # create uuid for user_id
        id = uuid.uuid1()
        id = id.int
        # make the id 12 digits
        id = str(id)
        id = id[:8]
        id = int(id)
        if is_business:
            user = User(user_id=id, username=username, email=email, password=password, private=False, is_business=True)
        else:
            user = User(user_id=id, username=username, email=email, password=password, private=False, is_business=False)
        db.session.add(user)
        db.session.commit()
        return user

    def update_user(self, user_id, username, password, email, about_me, private, profile_pic, banner_pic, first_name=None, last_name=None, is_business=None, address=None, city=None, state=None, zip_code=None, phone=None, website=None):
        '''Updates a user'''
        user = self.get_user_by_id(user_id)
        user.username = username
        user.password = password
        user.first_name = first_name
        user.last_name = last_name
        if email:
            user.email = email.lower()
        user.about_me = about_me
        if private == '1':
            user.private = True
        else:
            user.private = False

        user.profile_pic = profile_pic
        user.banner_pic = banner_pic

        # Business
        if is_business != None:
            user.address = address
            user.city = city
            user.state = state
            user.zip_code = zip_code
            user.phone = phone
            user.website = website

        db.session.commit()
        return user
    
    def update_location(self, user_id, lat, lng):
        '''Updates a user's location'''
        user = self.get_user_by_id(user_id)
        user.location = f'{lat},{lng}'
        db.session.commit()
        return user
    
    def search_user(self, search):
        '''Query user names and emails ignore case'''
        user = User.query.filter(User.username.ilike(f'%{search}%')).first()
        if user:
            return user
        return None
    
    def delete_user(self, user_id):
        '''Deletes a user'''
        user = self.get_user_by_id(user_id)
        user.email = "deleted"
        user.profile_pic = None
        user.banner_pic = None
        user.password = None
        db.session.commit()
        return user
    
    def clear(self):
        '''Clears all users'''
        User.query.delete()
        db.session.commit()

users = Users()