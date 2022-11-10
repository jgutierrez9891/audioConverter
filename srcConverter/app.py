from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from srcConverter.servicios.servicios import Converter
from srcConverter.modelos.modelos import db
import os

from google.cloud.sql.connector import Connector, IPTypes

# initialize Cloud SQL Python Connector object
instance_connection_name = "audioconverter-366014:us-central1:vinilosappdb" # e.g. 'project:region:instance'
db_user = "audioconverteru@audioconverter-366014.iam"  # e.g. 'my-db-user'
db_name = "flask_db"  # e.g. 'my-database'
ip_type = IPTypes.PUBLIC
connector = Connector()
def getconn():
    with Connector() as connector:
        conn = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            db=db_name,
            enable_iam_auth=True,
            ip_type=ip_type,
        )
        return conn

#Ruta donde se almacenan los archivos en enviados por el usuario (cambiar según ruta del OS por definir)
UPLOAD_FOLDER = '/mnt/files'


app = Flask(__name__)
app.config['EMAIL_API_KEY'] = ""
app.config['GCP_BUCKET_NAME'] = "audioconverter-files"
os.environ['GOOGLE_APPLICATION_CREDENTIALS']= '../../audioconverter-service-key.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "creator": getconn
}
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