# MISW4204_Projecto1_Entrega1 - CONVERSOR DE ARCHIVOS

Aplicación desarrollada en flask con Postgress DB, Redis y Celery

## Installation

Usar el manejador de paquetes [pip](https://pip.pypa.io/en/stable/) para instalar las dependencias, y recordemos activar nuestro ambiente de python

```bash
'source' venv/bin/activate

pip install -r requirements.txt
```

Debemos tener instalado de igual forma Docker [docker](https://www.docker.com/) para correr el contenedor de la base de datos, el Broker y El servicio Apache para exponer la carpeta donde se van a descargar los videos.

- En la carpeta de *dataBase*
```bash
docker-compose up -d
```

## Usage

- Debemos Abrir dos consolas y ejecutarlas en el siguiente orden

```bash 
celery -A app.celery_app worker -Q cola -n cola@worker --pool=solo -l info
```

```bash 
Flask run
```

## Authors

- Luis Alberto Cortes  
- Leonardo Barrios
- Sneyder Amado
- Juan David Calderón

## Version History

* 1.0
    * Release inicial
