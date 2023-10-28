import time
import calendar
import os
import errno
from celery import shared_task
from modelos import db, Tareas
from moviepy.editor import VideoFileClip # just import what you need
from datetime import datetime

formatosPermitidos = ["mp4", "webm", "avi", "mpeg", "wmv"]
videosPruebas = ["VideoCorto.mp4", ]

@shared_task(queue="cola", ignore_result=False)
def convertirArchivo(file, format, id_task):
    #Aqui se hace la conversión del archivo al nuevo formato, despues hay que cambiar el valor del estado de la tarea en la base de datos
    UpdateEstado(id_task, "in progress")    # Actualiza el registro de la tarea a in progress    
    format = format.replace('.','') # Elimina el punto de la extension en caso de que lo tenga
    conversion(file, format, id_task)
    UpdateEstado(id_task, "processed")    # Actualiza el registro de la tarea a processed    
    
def validacionArchivos(file, format):   
    result = ""
    format = format.replace('.','').lower() # Elimina el punto de la extension en caso de que lo tenga
        
    if format in formatosPermitidos:    # Valida que el formato enviado este dentro de los permitidos
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
    nombreArchivo = getNombreArchivo(fileName)[0]    
    video = VideoFileClip("archivos/" + str(id_task) + "/" + fileName).resize(0.1)
    if format == "mp4" or format == "wmv":
        video.write_videofile("archivos/" + str(id_task) + "/" + nombreArchivo + "." + format, codec="libx264")
    elif format == "webm":
        video.write_videofile("archivos/" + str(id_task) + "/" + nombreArchivo + "." + format, codec="libvpx")
    elif format == "avi":
        video.write_videofile("archivos/" + str(id_task) + "/" + nombreArchivo + "." + format, codec="png")
    elif format == "mpeg":
        video.write_videofile("archivos/" + str(id_task) + "/" + nombreArchivo + "." + format, codec="mpeg4")
    video.close()
    
def crearCarpeta(id_task):
    ruta = "archivos/" + str(id_task)
    try:
        os.mkdir(ruta)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return ruta + "/"
 
def guardarArchivo(file, id_task, fileName):
    file.save(os.path.join(crearCarpeta(id_task), fileName))
 
def getTimeStamp():
    current_GMT = time.gmtime() # time actual
    return calendar.timegm(current_GMT) # retorna el valor timeStamp

def getNombreArchivo(file):
    ruta = os.path.split(file) # divide la cadena file en ruta y nombre del archivo
    return os.path.splitext(ruta[1]) # retorna arreglo con el nombre del archivo y la extension

def crearTareaEnDB(file, format, fechaDeCreacion, userId):
    nueva_tarea = Tareas(nombre=file, convertirFormato = format, timeStampCarga=fechaDeCreacion, timeStampInicioProcesamiento = '', timeStampFinProcesamiento = '', tiempoProcesamiento = "",status='uploaded', usuario=userId)
    db.session.add(nueva_tarea)
    db.session.commit() # Crea la tarea en el base de datos      
    return db.session.query(Tareas).order_by(Tareas.id.desc()).first().id # Devuelve el id de la tarea creada
    
def UpdateEstado(id, estado):
    tarea = Tareas.query.filter(Tareas.id == id).first()
    if estado == 'in progress':
        tarea.timeStampInicioProcesamiento = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    else:
        tarea.timeStampFinProcesamiento = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                
        horaInicio = tarea.timeStampInicioProcesamiento.split(',')[1].strip()
        hHoraInicio = datetime.strptime(horaInicio, '%H:%M:%S')
        
        horaFin = tarea.timeStampFinProcesamiento.split(',')[1].strip()
        hHoraFin = datetime.strptime(horaFin, '%H:%M:%S')
        
        tarea.tiempoProcesamiento = hHoraFin - hHoraInicio
        
    tarea.status = estado
    db.session.commit()
