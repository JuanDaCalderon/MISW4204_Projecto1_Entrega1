import time
from celery import shared_task
from modelos import db, Tareas

@shared_task(queue="cola", ignore_result=False)
def convertirArchivo(file, format, id_task):
    #Aqui se hace la conversión del archivo al nuevo formato, despues hay que cambiar el valor del estado de la tarea en la base de datos
    time.sleep(20)
    tarea = Tareas.query.filter(Tareas.id == id_task).first()
    tarea.status = 'processed'
    db.session.commit()
    print('video ->', file)
    print('formato a convertir ->', format)