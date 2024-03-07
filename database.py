from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import JSON
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


class Database(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Database)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    name = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    keys = db.relationship('Keys', backref="owner", lazy=True)


class Keys(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class States(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    cities = db.relationship('Cities', backref="state_name", lazy=True)


class Cities(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state = db.Column(db.String, db.ForeignKey('states.name'), nullable=False)
    city = db.Column(db.String, nullable=False)
    json = db.Column(db.JSON, nullable=False)
