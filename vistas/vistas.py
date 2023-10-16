from flask import request
from flask_jwt_extended import jwt_required, create_access_token, decode_token, get_jwt_identity
from flask_restful import Resource
import hashlib
from datetime import datetime
from tareas import convertirArchivo

from modelos import \
    db, \
    Usuario, Tareas \

""" 
    VistaSignup
    POST
    Parametros: { username (String), password1 (String), password2 (String), email (String) } 
    Retorna: { mensaje }
"""
class VistaSignup(Resource):
    def post(self):
        usuario = Usuario.query.filter(Usuario.correo_electronico == request.json["email"]).first()
        if request.json["password1"] != request.json["password2"]:
            return "Las contraseñas no coinciden", 404
        elif usuario is None:
            contrasena_encriptada = hashlib.md5(request.json["password1"].encode('utf-8')).hexdigest()
            nuevo_usuario = Usuario(usuario=request.json["username"], correo_electronico=request.json["email"], password=contrasena_encriptada)
            db.session.add(nuevo_usuario)
            db.session.commit()
            return {"mensaje": "usuario creado exitosamente", "id": nuevo_usuario.id}
        else:
            return "El usuario ya existe con este correo", 404


""" 
    VistaLogin
    POST
    Parametros: { username (String), password (String) } 
    Retorna: { mensaje, token }
"""
class VistaLogin(Resource):
    def post(self):
        contrasena_encriptada = hashlib.md5(request.json["password"].encode('utf-8')).hexdigest()
        usuario = Usuario.query.filter(Usuario.usuario == request.json["username"], Usuario.password == contrasena_encriptada).first()
        db.session.commit()
        if usuario is None:
            return "El usuario no existe con estas credenciales", 404
        else:
            additional_claims = {"id": usuario.id, "username": usuario.usuario, "email": usuario.correo_electronico}
            token_de_acceso = create_access_token(identity=usuario.id, additional_claims=additional_claims)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso, "id": usuario.id}


""" 
    VistaTasks
    GET, POST
    Parametros de autorización: Bearer Token (String)
    Parametros de consulta: max (int), order (int) <- Asc:0 - Desc:1
    Parametros: { fileName (File), newFormat (String) } campo id, timeStamp, y status se generan de forma automática en la aplicación
    Retorna: { mensaje, tareas }
"""
class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        max = request.args.get("max")
        order = request.args.get("order")
        userId = get_jwt_identity()
        return {"tareas": ['todas las tareas listadas para este usuario'] , "maxFilter": max, "orderFilter": order}
    
    @jwt_required()
    def post(self):
        file = request.files['fileName']
        format = request.form["newFormat"]
        fechaDeCreacion = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        userId = get_jwt_identity()
        convertirArchivo.delay( file.filename , format) #Cola de tarea
        nueva_tarea = Tareas(nombre=file.filename, timeStamp=fechaDeCreacion, status='uploaded', usuario=userId)
        db.session.add(nueva_tarea)
        db.session.commit()
        return {
            "mensaje": 'se ha subido el archivo correctamente y en un tiempo la conversion sera completada para su descarga, por favor revisar en unos minutos',
            "archivo": file.filename,
            "Nuevo formato": format,
            "fecha Creacion": fechaDeCreacion,
            "id_Usuario": userId
        }


""" 
    VistaTask
    GET, DELETE
    Parametros Query: id_task
    Parametros de autorización: Bearer Token (String)
    Retorna: { mensaje, tarea: { archivoOriginal, archivoConvertido } }
"""
class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task):
        return { 
                "idTask": id_task,
                "mensaje": "Tarea con sus archivos recuperados correctamente",
                "tarea" : {
                    "archivoOriginal": 'https://url',
                    "archivoConvertido": 'https://url'
                }
            }
        
    @jwt_required()
    def delete(self, id_task):
        return { 
                "idTask": id_task,
                "mensaje": "Tarea eliminada correctamente"
            }