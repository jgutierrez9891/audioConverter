import json
from threading import Thread
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
import requests
from servicios.servicios import Converter
from modelos.modelos import db
import os

from google.cloud.sql.connector import Connector, IPTypes

from srcConverter.servicios.servicios import MessageListener

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

def consumer():
    """Receives messages from a pull subscription."""
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1

    project_id = "audioconverter-366014"
    subscription_id = "SuscriptorWorker"

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.")
        print(message.data.decode("utf-8").replace("'","\""))
        bodyAsJson = json.loads(message.data.decode("utf-8").replace("'","\""))
        x = requests.post (url = "http://127.0.0.1:8081/api/convert",json = bodyAsJson)
        message.ack()
        print("Done")

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    with subscriber:
        try:
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.


app = Flask(__name__)


app.config['EMAIL_API_KEY'] = os.environ['EMAIL_API_KEY']
app.config['GCP_BUCKET_NAME'] = "audioconverter-files"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "creator": getconn
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
api.add_resource(Converter, '/api/convert')
api.add_resource(MessageListener, '/api/listeMessage')

jwt = JWTManager(app)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)