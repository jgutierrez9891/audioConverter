
# audioConverter

  
## Descripción
audioConverter es una solución construida en Python que permite a los usuarios solicitar la conversión de archivos multimedia de audio entre formatos **mp3**, **ogg** y **wav**
La aplicación permite a los usuarios realizar el proceso de registro, para luego autenticarse y obtener un token que debe ser usado para poder acceder a los diferentes recursos que le permiten solicitar la conversión de sus archivos a diferentes formatos.
audioConverter usa tecnología **Flask** para los API REST, base de datos **Postgresql**. Para el procesamiento de los archivos a convertir se construyó una solución asíncrona que recibe las solicitudes de conversión en una cola **rabbitMQ**; un componente converter se suscribe a ella para realizar el procesamiento de cada uno de los archivos usando la biblioteca **PyDub** (usa la librería **ffMPEg** del sistema operativo), se envía una notificación de correo usando la biblioteca **yagmail** al usuario que solicitó la conversión indicando que su archivo esta listo y finalmente actualiza el registro de tarea de conversión en la base de datos.
 
## Instrucciones para la instalación
Las siguientes instrucciones para instalación de la solución aplican para una máquina con sistema operativo **Linux Debian 11.5**

## ON PREMISE

### Prerequisitos on premise
Se deben cumplir los siguientes prerequisitos para el correcto funcionamiento de la solución:
 1. Base de datos **Postgres** con un esquema llamado ***flask_db***
 2. Message broker **RabbitMQ** ejecutando y con una cola configurada así:
	 - Tipo: Clásica
	 - Nombre: ***conversion_processs***
	 - Durabilidad: Durable
	 - Auto borrado: NO
3. **Python 3.9** instalado
4. Entorno virtual de Python instalado. En la línea de comandos ejecute:
>sudo apt-get install python3-venv
6. **Git** instalado

### Pasos para la instalación On Premise
 1. Instalar la librería **ffMPEg**. En una terminal ejecute:
 >sudo apt install ffmpeg
 2. Descargar el repositorio usando 
>git clone https://github.com/jgutierrez9891/audioConverter.git
 3. Moverse a la carpeta del directorio. En una terminal ejecute:
>cd audioConverter
 5. Instalar el entorno virtual de Python. En la terminal ejecute:
>python3 -m venv env
 7. Active el entorno virtual de Python. En la terminal ejecute:
>source env/bin/activate
 9. Instale las dependencias del proyecto. En la terminal ejecute:
> python3 -m pip install -r requirements.txt
 11. En una nueva terminal inicie el API Flask. Ubiquese en la carpeta del proyecto que descargo de git (*audioConverter*) y ejecute los siguientes comandos:
> cd src
>
> flask run -p 3000
12. En una nueva terminal inicie el componente de notificaciones. Ejecute los siguientes comandos:
>cd srcNotifications
>
>flask run -p 4000
13. En una nueva terminal inicie el componente convertidor. Ejecute los siguientes comandos:
>cd srcConverter
>
>flask run -p 5000
14. En una nueva terminal inicie el componente de conexión a la cola para conversión. Ejecute los siguientes comandos:
>cd src
>
>python3 consumer.py

## CLOUD

### Prerequisitos Cloud
Se deben cumplir los siguientes prerequisitos para el correcto funcionamiento de la solución:
 1. Base de datos **Postgres** con un esquema llamado ***flask_db***
 2. Creacion de una maquina que funcione como un nfs y configuracion con carpeta y ruta para guardar tanto los archivos de subida como los archivos para descarga
 3. 2 maquinas virtuales ambas corriendo con sistema operativo **Linux Debian 11.5**, una para el api y la otra para el worker
 4. Tener git instalado en ambas maquinas
 5. configurar en la maquina del worker el Message broker **RabbitMQ** ejecutando y con una cola configurada así:
	 - Tipo: Clásica
	 - Nombre: ***conversion_processs***
	 - Durabilidad: Durable
	 - Auto borrado: NO
6. **Python 3.9** instalado en ambas maquinas
7. Realizar instalacion de Entorno virtual de Python en ambas maquinas. En la línea de comandos ejecute:
>sudo apt-get install python3-venv

### Pasos para la instalación Cloud
 1. Configurar tanto en la maquina del api como en el worker la conexion con el nfs: (CARLOS) 
 2. Instalar en la maquina worker la librería **ffMPEg**. En una terminal ejecute:
 >sudo apt install ffmpeg
 3. Descargar el repositorio en ambas maquinas usando 
 >git clone https://github.com/jgutierrez9891/audioConverter.git
 4. Instalar la CLI de GCP usando los pasos de la siguiente guia: 
 >https://cloud.google.com/sdk/docs/install-sdk 
 5. Instalar el proxy de autenticación de Cloud SQL usando los pasos de la siguiente guia: 
 >https://cloud.google.com/sql/docs/postgres/quickstart-proxy-test
 6. Moverse a la carpeta del directorio en ambas maquinas. En una terminal ejecute:
 >cd audioConverter
 7. Instalar el entorno virtual de Python en ambas maquinas. En la terminal ejecute:
 >python3 -m venv env
 8. Active el entorno virtual de Python en ambas maquinas. En la terminal ejecute:
 >source env/bin/activate
 9. Instale las dependencias del proyecto en ambas maquinas. En la terminal ejecute:
 > python3 -m pip install -r requirements.txt
 10. En la maquina API abra una nueva terminal e inicie el API Flask. Ubiquese en la carpeta del proyecto que descargo de git (*audioConverter*) y ejecute los  siguientes comandos:
 > cd src
 >
 > flask run -p 3000
 11. En la maquina Worker abra una nueva terminal e inicie el convertidor Flask. Ejecute los siguientes comandos:
 >cd srcConverter
 >
 >flask run -p 5000
 12. En la maquina Worker abra una nueva terminal e inicie la cola. Ejecute los siguientes comandos:
 >cd src
 >
 >sudo docker run --rm -it -p 15672:15672 -p 5672:5672 rabbitmq:3-management
 13. En una nueva terminal inicie el componente de conexión a la cola para conversión. Ejecute los siguientes comandos:
 >cd src
 >
 >python3 consumer.py


