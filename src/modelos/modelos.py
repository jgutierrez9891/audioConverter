from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String())
    newFormat = db.Column(db.String())
    timeStamp = db.Column(db.DateTime())
    status = db.Column(db.String())
    conversionTimeStamp = db.Column(db.DateTime())
    secondsTakedToStartConversion = db.Column(db.Integer)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    email = db.Column(db.String())
    tasks = db.relationship('Task', cascade='all, delete, delete-orphan')