from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from srcConverter.servicios.servicios import Converter
from srcConverter.modelos.modelos import db

#Ruta donde se almacenan los archivos en enviados por el usuario (cambiar según ruta del OS por definir)
UPLOAD_FOLDER = 'C:\\ruta'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Grupo21@127.0.0.1:5433/flask_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_SECRET_KEY'] = 'm723984iefwkjp09480kdjsdhsd7nenkjcsd'

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.drop_all()
db.create_all()

api = Api(app)
api.add_resource(Converter, '/api/convert')

jwt = JWTManager(app)