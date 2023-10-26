from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    correo_electronico = db.Column(db.String(50))
    password = db.Column(db.String(50))
    

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        include_fk = True
        load_instance = True
    id = fields.Integer()
    usuario=fields.String()
    correo_electronico = fields.String()
    password = fields.String()
    
class Tareas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    convertirFormato = db.Column(db.String(128))
    timeStampCarga = db.Column(db.String(128))
    timeStampInicioProcesamiento = db.Column(db.String(128))
    timeStampFinProcesamiento = db.Column(db.String(128))
    tiempoProcesamiento = db.Column(db.String(128))
    status = db.Column(db.String(128))
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))


class TareasSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tareas
        include_relationships = True
        include_fk = True
        load_instance = True
    id = fields.Integer()
    nombre = fields.String()
    convertirFormato = fields.String()
    timeStampCarga = fields.String()
    timeStampInicioProcesamiento = fields.String()
    timeStampFinProcesamiento = fields.String()
    tiempoProcesamiento = db.Column(db.String(128))
    stastus = fields.String()
