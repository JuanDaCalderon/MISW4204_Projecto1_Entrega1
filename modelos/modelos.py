from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    correo_electronico = db.Column(db.String(50))
    password = db.Column(db.String(50))
    
class Tareas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    convertirFormato = db.Column(db.String(128))
    timeStamp = db.Column(db.String(128))
    status = db.Column(db.String(128))
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
