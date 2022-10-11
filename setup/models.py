from setup import db
from datetime import datetime, timedelta
from flask import current_app, url_for
# For pwd verification, the following are imported
from werkzeug.security import check_password_hash, generate_password_hash
from hashlib import md5
# For jwt token
import jwt
from time import time
import json
# For API tokens
import base64
import os


class PaginatedAPIMixin():
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False) #Paginate obj with items attr.
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page+1, per_page=per_page, **kwargs)
                if resources.has_next else None,
                'prev': url_for(endpoint, page=page-1, per_page=per_page, **kwargs)
                if resources.has_prev else None
            }
        }
        return data



class User(PaginatedAPIMixin, db.Model):
    # Create a User object for mapping to the "users" table in the SQL db
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default = datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    phone_no = db.Column(db.String(20))
    
    # Attrs. for API tokens
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    # Attr for donation
    donations = db.relationship('Donation', backref='donor', lazy='dynamic')

    def __repr__(self) -> str:
        return f"<User {self.username}>" 

    def set_password(self, password):
        # Set the pwd_hash attr. to  the password_hash generated with the password given  
        self.password_hash = generate_password_hash(password = password)
    
    def check_password(self, password):
        # Returns True if the password provided by the user matches the hash
        return check_password_hash(self.password_hash, password)
    
    
    def get_reset_password_token(self, expires_in=600):
        # Generate a JWT token with payload as the user id
        token = jwt.encode(
            { "reset_password": self.id, "exp": time() + expires_in}, current_app.config['SECRET_KEY'],algorithm='HS256'
        )
        return token
    
    @staticmethod
    def verify_reset_password_token(token):
        # Use a try, except to catch errors and then get the corresponding User obj.
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'email': self.email,
            'is_admin': self.is_admin,
            'phone_no': self.phone_no,
            '_links': {
                'self': url_for('api.get_user', id=self.id),
            }
        }     
        return data
    
    def from_dict(self, data):
        for field in ['username', 'email', 'phone_no']:
            if field in data:
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


class Orphanage(db.Model, PaginatedAPIMixin):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    students = db.Column(db.Integer)
    phone_no = db.Column(db.String(20))
    location = db.Column(db.JSON)
    activities = db.Column(db.Text)
    paypal_info = db.Column(db.JSON)
    social_media_links = db.Column(db.JSON)
    story = db.Column(db.Text)
    money_uses = db.Column(db.Text)
    photos_links = db.Column(db.JSON)
    bank_info = db.Column(db.Text)
    actId = db.Column(db.String(120))
    acttype = db.Column(db.String(6))
    country = db.Column(db.String(90))
    good_work = db.Column(db.Text)
    monthly_donation = db.Column(db.String(90))
    registration_certificate = db.Column(db.String(250))
    blog_link = db.Column(db.String(250))
    donations = db.relationship('Donation', backref='recipient', lazy='dynamic')

    def __repr__(self):
        return f"<Orphanage {self.name}- {self.students} students>"

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'students': self.students,
            'phone_no': self.phone_no,
            'location': self.location,
            'activities': self.activities,
            'paypal_info': self.paypal_info,
            'social_media_links': self.social_media_links,
            'story': self.story,
            'money_uses': self.money_uses,
            'photos_links': self.photos_links,
            'bank_info': self.bank_info,
            'actId': self.actId,
            'acttype': self.acttype,
            'country': self.country,
            'good_work': self.good_work,
            'monthly_donation': self.monthly_donation,
            'registration_certificate': self.registration_certificate,
            'blog_link': self.blog_link,
            '_links': {
                'self': url_for('api.get_orphanage', id=self.id),
            }
        }
        return data

    def from_dict(self, data):
        columns = ['name', 'email', 'students', 'phone_no', 'location', 'activities', 'paypal_info', 'social_media_links',
                   'story', 'money_uses', 'photos_links','bank_info','actId','acttype','country','good_work',
                   'monthly_donation', 'registration_certificate', 'blog_link']
        for field in columns:
            if field in data:
                setattr(self, field, data[field])
        
class Message(db.Model, PaginatedAPIMixin):
    id = db.Column(db.Integer,primary_key = True)
    first_name = db.Column(db.String(64), index = True)
    last_name = db.Column(db.String(64), index = True)
    email = db.Column(db.String(120))
    phone_no = db.Column(db.String(20))
    content = db.Column(db.Text)
    creation_datetime = db.Column(db.DateTime, default = datetime.utcnow)

    def from_dict(self, data):
        for field in ['first_name', 'last_name','email', 'phone_no', 'content']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_no': self.phone_no,
            'content': self.content,
            'creation_datetime': self.creation_datetime
        }
        return data

class Donation(db.Model):
    #id, amt, timestamp, user(donor), orphanage(recipient)
    id = db.Column(db.Integer,primary_key = True)
    donation_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    amount = db.Column(db.Numeric(12,2))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    orph_id = db.Column(db.Integer, db.ForeignKey('orphanage.id'))

    def __repr__(self):
        return f"<Donation- {self.amount} donated by {self.donor.username} to {self.recipient.name}>"

    def to_dict(self):
        data = {
            'donation_time': self.donation_time,
            'amount': float(self.amount),
            'donor': self.donor.username,
            'recipient_orphanage': self.recipient.name
        }
        return data
        

