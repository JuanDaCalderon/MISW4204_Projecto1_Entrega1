# MISW4204_Projecto1_Entrega1
## CONVERSOR DE ARCHIVOS
Aplicación desarrollada en flask con Postgress DB, Redis y Celery


# Pasos para lanzar la aplicación

## Lanzar el redis
redis-server <- WSL Ubuntu

## Cola
celery -A app.celery_app worker -Q cola -n cola@worker --pool=solo -l info

## Lanzar aplicación
Flask run