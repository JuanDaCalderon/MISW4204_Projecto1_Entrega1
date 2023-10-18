from flask import request
from flask_jwt_extended import jwt_required, create_access_token, decode_token, get_jwt_identity
from flask_restful import Resource
import hashlib
from datetime import datetime
from tareas import convertirArchivo, validacionArchivos, crearTareaEnDB
from werkzeug.utils import secure_filename

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
    def get(self): #Sneyder
        max = request.args.get("max")
        order = request.args.get("order")
        userId = get_jwt_identity()
        return {"tareas": ['todas las tareas listadas para este usuario'] , "maxFilter": max, "orderFilter": order}
    
    @jwt_required()
    def post(self): #Luis
        file = request.files['fileName']
        nombreArchivo = secure_filename(file.filename)
        print("*****Archivo:" + nombreArchivo)
        
        #format = request.form["newFormat"]
        
        #file = request.json['fileName']
        #format = request.json["newFormat"]
        
        '''validacion = validacionArchivos(file, format)
        
        if validacion != "":
            return "{ validacion }"            
        else:
            fechaDeCreacion = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            userId = get_jwt_identity()
            id = crearTareaEnDB(file, format, fechaDeCreacion, userId)  # Crea la tarea en la DB y trae el ID para poder actualizar el registro despues de la conversion
            convertirArchivo.delay( file , format, id) #Cola de tarea
            
            return {
                "mensaje": 'se ha subido el archivo correctamente y en un tiempo la conversion sera completada para su descarga, por favor revisar en unos minutos',
                "archivo": file,
                "Nuevo formato": format,
                "fecha Creacion": fechaDeCreacion,
                "id_Usuario": userId
            }'''


""" 
    VistaTask
    GET, DELETE
    Parametros Query: id_task
    Parametros de autorización: Bearer Token (String)
    Retorna: { mensaje, tarea: { archivoOriginal, archivoConvertido } }
"""
class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task): #Juanda
        idTask = id_task
        userId = get_jwt_identity()
        tarea = Tareas.query.filter(Tareas.id == idTask, Tareas.usuario == userId).first()
        if tarea is None:
            return { "mensaje": "No existe una tarea con este id" }, 404
        elif tarea.status == 'uploaded':
            return { "mensaje": "Aun no se ha terminado de convertir el archivo, vuelve a intentarlo mas tarde" }
        else:
            archivoOriginal = str(tarea.nombre)
            archivoConvertido = str(str(tarea.nombre).split(".")[0].lower() + '.' + tarea.convertirFormato).lower()
            path = 'archivos/' + str(tarea.id) + '/'
            return { 
                    "id": idTask,
                    "mensaje": "Archivos recuperados exitosamente",
                    "tarea" : {
                        "archivoOriginal": path + archivoOriginal,
                        "archivoConvertido": path + archivoConvertido,
                        "url de descarga": 'https://www.adslzone.net/app/uploads-adslzone.net/2019/04/borrar-fondo-imagen-1200x675.jpg'
                    }
                }
        
    @jwt_required()
    def delete(self, id_task): # Leo
        return { 
                "idTask": id_task,
                "mensaje": "Tarea eliminada correctamente"
            }