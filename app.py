from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from dotenv import load_dotenv
load_dotenv('.env')
from os import environ
from celery import Celery, Task
from modelos import db
from vistas import \
    VistaSignup, VistaLogin, \
    VistaTasks, VistaTask 
import argparse
from typing import Optional
from tareas import convertirArchivo
from google.cloud import pubsub_v1


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+environ.get('PGSQL_USER')+':'+environ.get('PGSQL_PASSWORD')+'@'+environ.get('PGSQL_HOST')+'/'+ environ.get('PGSQL_DB')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://"+environ.get('REDIS_SERVER')+":6379/0",
        result_backend="redis://"+environ.get('REDIS_SERVER')+":6379/0",
        task_ignore_result=True
    ),
)

celery_app = celery_init_app(app)

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)
api = Api(app)

api.add_resource(VistaSignup, '/api/auth/signup') #POST
api.add_resource(VistaLogin, '/api/auth/login') #POST
api.add_resource(VistaTasks, '/api/tasks') #GET, POST
api.add_resource(VistaTask, '/api/tasks/<int:id_task>') #GET, DELETE

jwt = JWTManager(app)

def sub(project_id: str, subscription_id: str, timeout: Optional[float] = None) -> None:
    """Receives messages from a Pub/Sub subscription."""
    # Initialize a Subscriber client
    subscriber_client = pubsub_v1.SubscriberClient()
    # Create a fully qualified identifier in the form of
    # `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber_client.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.")
        datos = str(message.data).split(',')
        print(f"Received {datos}")
        datos[0] = datos[0].replace("b'","")
        datos[2] = datos[2].replace("'","")
        print(f"Received {datos[0], datos[1], int(datos[2])}")
        convertirArchivo(datos[0], datos[1], int(datos[2]))
        # Acknowledge the message. Unack'ed messages will be redelivered.
        message.ack()
        print(f"Acknowledged {message.message_id}.")

    streaming_pull_future = subscriber_client.subscribe(
        subscription_path, callback=callback
    )
    print(f"Listening for messages on {subscription_path}..\n")

    try:
        # Calling result() on StreamingPullFuture keeps the main thread from
        # exiting while messages get processed in the callbacks.
        streaming_pull_future.result(timeout=timeout)
    except:  # noqa
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.

    subscriber_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_id", help="Google Cloud project ID")
    parser.add_argument("subscription_id", help="Pub/Sub subscription ID")
    parser.add_argument(
        "timeout", default=None, nargs="?", const=1, help="Pub/Sub subscription ID"
    )

    args = parser.parse_args()

    sub(args.project_id, args.subscription_id, args.timeout)
