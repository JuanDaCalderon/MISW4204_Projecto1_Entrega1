import time
from celery import Celery

celery_app = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0',)

# se crea metodo con cola para la conversion y guardado del archivo
@celery_app.task(queue="cola")
def convertirArchivo(file, format):
    #Aqui se hace la conversión del archivo al nuevo formato, despues hay que cambiar el valor del estado de la tarea en la base de datos
    time.sleep(10)
    print('video ->', file)
    print('formato a convertir ->', format)
