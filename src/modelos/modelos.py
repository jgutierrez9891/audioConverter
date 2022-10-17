from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String())
    newFormat = db.Column(db.String())
    timeStamp = db.Column(db.DateTime())
    status = db.Column(db.String())