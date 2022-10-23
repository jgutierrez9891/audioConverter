from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from src.servicios.servicios import Auth, AuthLogin, TaskR, Tasks
from src.modelos.modelos import db
from pathlib import Path

#Ruta donde se almacenan los archivos en enviados por el usuario (cambiar según ruta del OS por definir)
data_folder = Path("C:/ruta")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = data_folder
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/flask_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_SECRET_KEY'] = 'm723984iefwkjp09480kdjsdhsd7nenkjcsd'

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.drop_all()
db.create_all()

api = Api(app)
api.add_resource(Tasks, '/api/tasks', '/api/tasks/<order>', '/api/tasks/<order>/<maxel>')
api.add_resource(Auth, '/api/auth/signup')
api.add_resource(AuthLogin, '/api/auth/login')
api.add_resource(TaskR, '/api/tasks/<userid>')

jwt = JWTManager(app)