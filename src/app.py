from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from src.servicios.servicios import Tasks
from src.modelos.modelos import db

#Ruta donde se almacenan los archivos en enviados por el usuario (cambiar según ruta del OS por definir)
UPLOAD_FOLDER = 'C:\\Users\\joal9\\Documents'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/flask_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.drop_all()
db.create_all()

api = Api(app)
api.add_resource(Tasks, '/tasks')

