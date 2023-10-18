import time
import calendar
import os
import subprocess
import ffmpeg
import errno
from celery import shared_task
from datetime import datetime
from flask_jwt_extended import jwt_required, create_access_token, decode_token, get_jwt_identity
from modelos import db, Tareas

formatosPermitidos = ["mp4", "webm", "avi", "mpeg", "wmv"]

@shared_task(queue="cola", ignore_result=False)
def convertirArchivo(file, format, id_task):
    #Aqui se hace la conversión del archivo al nuevo formato, despues hay que cambiar el valor del estado de la tarea en la base de datos
    format = format.replace('.','') # Elimina el punto de la extension en caso de que lo tenga
    archivoExtension = getNombreArchivo(file) # trae el nombre del archivo y la extension en un arreglo
    
    conversion(file, format, id_task)

    UpdateEstado(id_task)    # Actualiza el registro de la tarea    


    
def validacionArchivos(file, format):   
    result = ""
    format = format.replace('.','') # Elimina el punto de la extension en caso de que lo tenga
        
    if format.lower() in formatosPermitidos:    # Valida que el formato enviado este dentro de los permitidos
        extensionArchivo = (getNombreArchivo(file)[1]).replace('.','') # Trae la extension del archivo de origen
        if extensionArchivo.lower() in formatosPermitidos: # Valida que el formato del archivo enviado este dentro de los permitidos
            if format == extensionArchivo:         
                result = "El formato de destino es el mismo que el formato de origen" 
        else:
            result = "El formato del archivo no es valido" 
    else: 
        result = "El formato de destino no es valido"
        
    return result


def conversion(fileName, format, id_task):
    try:
        os.mkdir("archivos/" + str(id_task))
    except OSError as e:
        if e.erno != errno.EEXIST:
            raise
    nombreArchivo = getNombreArchivo(fileName)[0]    
    (
        ffmpeg.input(fileName)
        .output("archivos/" + str(id_task) + "/" + nombreArchivo + "." + format)
        .run()
    )
    return "Hecho"
 
def getTimeStamp():
    current_GMT = time.gmtime() # time actual
    return calendar.timegm(current_GMT) # retorna el valor timeStamp

def getNombreArchivo(file):
    ruta = os.path.split(file) # divide la cadena file en ruta y nombre del archivo
    return os.path.splitext(ruta[1]) # retorna arreglo con el nombre del archivo y la extension

def crearTareaEnDB(file, format, fechaDeCreacion, userId):
    nueva_tarea = Tareas(nombre=file, convertirFormato = format, timeStamp=fechaDeCreacion, status='uploaded', usuario=userId)
    db.session.add(nueva_tarea)
    db.session.commit() # Crea la tarea en el base de datos   
    return db.session.query(Tareas).order_by(Tareas.id.desc()).first().id # Devuelve el id de la tarea creada
    
def UpdateEstado(id):
    tarea = Tareas.query.filter(Tareas.id == id).first()
    tarea.status = 'processed'
    db.session.commit()

    