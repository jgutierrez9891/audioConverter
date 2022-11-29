from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from servicios.servicios import MessageListener
from modelos.modelos import db
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

app = Flask(__name__)


app.config['EMAIL_API_KEY'] = os.environ['EMAIL_API_KEY']
app.config['GCP_BUCKET_NAME'] = "audioconverter-files"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "creator": getconn,
    "pool_size": 30
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_SECRET_KEY'] = 'm723984iefwkjp09480kdjsdhsd7nenkjcsd'
app.config['PUBSUB_VERIFICATION_TOKEN'] = os.environ['PUBSUB_VERIFICATION_TOKEN']
app.config['PUBSUB_TOPIC'] = os.environ['PUBSUB_TOPIC']

app_context = app.app_context()
app_context.push()

db.init_app(app)

api = Api(app)
api.add_resource(MessageListener, '/api/listenerMessage')

jwt = JWTManager(app)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)