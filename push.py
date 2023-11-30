from flask import Flask, request, abort
from google.cloud import pubsub_v1
import tareas 
from dotenv import load_dotenv
load_dotenv('.env')
from os import environ
from modelos import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+environ.get('PGSQL_USER')+':'+environ.get('PGSQL_PASSWORD')+'@'+environ.get('PGSQL_HOST')+'/'+ environ.get('PGSQL_DB')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()


# Configura las credenciales de Google Cloud
# Debes configurar GOOGLE_APPLICATION_CREDENTIALS en tu entorno o proporcionar el archivo de credenciales.
# Más información: https://cloud.google.com/docs/authentication/getting-started
publisher = pubsub_v1.PublisherClient()

# Nombre del tema y la suscripción de Pub/Sub
topic_name = 'backend-flask'
subscription_name = 'worker'

# Ruta para recibir mensajes push
push_endpoint = '/push-video'

# Crea una suscripción si no existe
try:
    subscriber = pubsub_v1.SubscriberClient()
    subscriber.create_subscription(name=subscription_name, topic=topic_name)
except Exception as e:
    print(f"Error al crear la suscripción: {e}")

# Configura la ruta de recepción de mensajes push
@app.route(push_endpoint, methods=['POST'])
def receive_push():
    try:
        # Verifica la autenticación del servicio de Pub/Sub
        '''token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            abort(401, 'Unauthorized') '''

        # Verifica la firma de la solicitud (opcional pero recomendado para seguridad)
        # Más información: https://cloud.google.com/pubsub/docs/push#verifying-signatures
        # Puedes implementar la lógica de verificación de firma según tus necesidades de seguridad.

        # Procesa el mensaje recibido
        message = request.get_data()
        print(f"Mensaje recibido: {message}")
        datos = str(message).split(',')
        datos[0] = datos[0].replace("b'","")
        datos[2] = datos[2].replace("'","")
        print(f"Received {datos[0], datos[1], int(datos[2])}")

        # Realiza cualquier lógica de procesamiento necesario aquí
        
        tareas.convertirArchivo(datos[0], datos[1], int(datos[2]),app_context)

        return 'procesado ...', 204  # 204 significa "No Content" para indicar que la solicitud fue procesada correctamente

    except Exception as e:
        print(f"Error al procesar la solicitud push: {e}")
        abort(500, 'Internal Server Error')

if __name__ == '__main__':
    
    
    app.run(host='0.0.0.0', port=8080, debug=True)