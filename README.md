# MISW4204_Projecto1_Entrega1
MISW4204 Desarrollo de software en la nube

## Lanzar el redis
redis-server <- WSL Ubuntu

## Cola
celery -A app.celery_app worker -Q cola -n cola@worker --pool=solo -l info

## Lanzar aplicación
Flask run