import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from src.servicios.servicios import Auth, AuthLogin, TaskR, Tasks, FilesR

from src.modelos.modelos import db
from pathlib import Path

from google.cloud.sql.connector import Connector, IPTypes

# initialize Cloud SQL Python Connector object
instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]  # e.g. 'project:region:instance'
db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
connector = Connector()
def getconn():
    with Connector() as connector:
        conn: connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            db=db_name,
            enable_iam_auth=True,
            ip_type=ip_type,
        )
        return conn

#Ruta donde se almacenan los archivos en enviados por el usuario (cambiar según ruta del OS por definir)
data_folder = Path("/mnt/files")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = data_folder
os.environ['GOOGLE_APPLICATION_CREDENTIALS']= '../../audioconverter-service-key.json'
app.config['GCP_BUCKET_NAME'] = "audioconverter-files"
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
api.add_resource(Tasks, '/api/tasks')
api.add_resource(Auth, '/api/auth/signup')
api.add_resource(AuthLogin, '/api/auth/login')
api.add_resource(TaskR, '/api/tasks/<taskId>')
api.add_resource(FilesR, '/api/files/<filename>')

jwt = JWTManager(app)