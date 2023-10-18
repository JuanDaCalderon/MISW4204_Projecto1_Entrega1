from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from dotenv import load_dotenv
load_dotenv('.env')
from os import environ
from modelos import db
from vistas import \
    VistaSignup, VistaLogin, \
    VistaTasks, VistaTask \



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+environ.get('PGSQL_USER')+':'+environ.get('PGSQL_PASSWORD')+'@'+environ.get('PGSQL_HOST')+'/'+ environ.get('PGSQL_DB')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

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
