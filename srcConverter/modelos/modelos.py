from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String())
    newFormat = db.Column(db.String())
    timeStamp = db.Column(db.DateTime())
    status = db.Column(db.String())

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    email = db.Column(db.String())