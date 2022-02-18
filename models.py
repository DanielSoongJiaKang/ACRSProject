from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class UserAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime(timezone=True), default = func.now())
    email = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    action = db.Column(db.String(150))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    roles = db.Column(db.String(30))
    name = db.Column(db.String(50))
    contact = db.Column(db.String(8))
    status = db.Column(db.String(8))
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    likes = db.relationship('LikePost', backref='user', passive_deletes=True)
    audit = db.relationship('UserAudit', backref='user', passive_deletes=True)
    entry = db.relationship('EntryVehicle', backref='user', passive_deletes=True)


#    entry = db.relationship('EntryVehicle', backref='user')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    likes = db.relationship('LikePost', backref='post', passive_deletes=True)
    category = db.Column(db.String(15))
    status = db.Column(db.String(15))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)

class EntryVehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime(timezone=True), default = func.now())
    vehicleno = db.Column(db.String(15))
    email = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    access = db.Column(db.String(40))


class LikePost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicleno = db.Column(db.String(15), unique = True)
    holdername = db.Column(db.String(150))
    holdertype = db.Column(db.String(150))
    model = db.Column(db.String(150))
    company = db.Column(db.String(150))





class VehicleAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicleno = db.Column(db.String(15))
    datetimescanned = db.Column(db.DateTime(timezone=True), default = func.now())
    name = db.Column(db.String(40))
    status = db.Column(db.String(40))
    numofcaught = db.Column(db.Integer)



class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventname = db.Column(db.String(120))
    startdate = db.Column(db.DateTime(timezone=True), default = func.now())
    enddate = db.Column(db.DateTime(timezone=True), default = func.now())
    colorcode = db.Column(db.String(30))
    eventtype = db.Column(db.String(40))
    eventdes = db.Column(db.String(200))


class TrackVehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicleno = db.Column(db.String(15))
    startdatetime= db.Column(db.DateTime(timezone=True))
    enddatetime= db.Column(db.DateTime(timezone=True))
    duration = db.Column(db.Integer)
    name = db.Column(db.String(40))

class Appeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicleno = db.Column(db.String(15))
    email = db.Column(db.String(150))
    reason = db.Column(db.String(2000))
    name = db.Column(db.String(150))











