
# audioConverter

  
## Descripción
audioConverter es una solución construida en Python que permite a los usuarios solicitar la conversión de archivos multimedia de audio entre formatos **mp3**, **ogg** y **wav**
La aplicación permite a los usuarios realizar el proceso de registro, para luego autenticarse y obtener un token que debe ser usado para poder acceder a los diferentes recursos que le permiten solicitar la conversión de sus archivos a diferentes formatos.
audioConverter usa tecnología **Flask** para los API REST, base de datos **Postgresql**. Para el procesamiento de los archivos a convertir se construyó una solución asíncrona que recibe las solicitudes de conversión en una cola **rabbitMQ**; un componente converter se suscribe a ella para realizar el procesamiento de cada uno de los archivos usando la biblioteca **PyDub** (usa la librería **ffMPEg** del sistema operativo), se envía una notificación de correo usando la biblioteca **yagmail** al usuario que solicitó la conversión indicando que su archivo esta listo y finalmente actualiza el registro de tarea de conversión en la base de datos.
 
## Instrucciones para la instalación
Las siguientes instrucciones para instalación de la solución aplican para una máquina con sistema operativo **Linux Debian 11.5**

### Prerequisitos
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

### Pasos para la instalación
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


