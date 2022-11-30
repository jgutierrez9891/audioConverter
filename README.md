# audioConverter

  
## Descripción
audioConverter es una solución construida en Python que permite a los usuarios solicitar la conversión de archivos multimedia de audio entre formatos **mp3**, **ogg** y **wav**
La aplicación permite a los usuarios realizar el proceso de registro, para luego autenticarse y obtener un token que debe ser usado para poder acceder a los diferentes recursos que le permiten solicitar la conversión de sus archivos a diferentes formatos.
audioConverter usa tecnología **Flask** para los API REST, base de datos **Postgresql**. Para el procesamiento de los archivos a convertir se construyó una solución asíncrona; un componente converter realiza el procesamiento de cada uno de los archivos usando la biblioteca **PyDub** (usa la librería **ffMPEg** del sistema operativo), se envía una notificación de correo al usuario que solicitó la conversión indicando que su archivo esta listo y finalmente actualiza el registro de tarea de conversión en la base de datos.
 
## Instrucciones para la instalación
Las siguientes instrucciones para instalación de la solución aplican para una máquina con sistema operativo **Linux Debian 11.5**

# ON PREMISE

[Release](https://github.com/jgutierrez9891/audioConverter/releases/tag/v1.0.0)
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

# CLOUD

## Iteración 1 básica

[Release](https://github.com/jgutierrez9891/audioConverter/releases/tag/v1.1.0)

### Prerequisitos Cloud
Se deben cumplir los siguientes prerequisitos para el correcto funcionamiento de la solución:
 1. Base de datos **Postgres** con un esquema llamado ***flask_db***, ejecutando en una instancia de base de datos del servicio cloud de SQL de GCP.
 2. Creacion de una máquina que funcione como un nfs y configuracion con carpeta y ruta para guardar tanto los archivos de subida como los archivos para descarga
 3. 2 máquinas virtuales ambas corriendo con sistema operativo **Linux Debian 11.5**, una para el api y la otra para el worker
 4. Tener git instalado en ambas máquinas
 5. Configurar en la máquina del worker el Message broker **RabbitMQ** ejecutando y con una cola configurada así:
	 - Tipo: Clásica
	 - Nombre: ***conversion_processs***
	 - Durabilidad: Durable
	 - Auto borrado: NO
6. **Python 3.9** instalado en ambas máquinas
7. Realizar instalacion de Entorno virtual de Python en ambas máquinas. En la línea de comandos ejecute:
>sudo apt-get install python3-venv

### Pasos para la instalación Cloud
 1. Configurar tanto en la máquina del api como en el worker la conexion con el nfs donde se deben reemplazar nfs-ip, carpetaComaprtida y carpetaLocal por los valores correspondientes a ip y rutas respectivamente:
 >apt-get install nfs-common -y
 >mount nfs-ip:carpetaComaprtida carpetaLocal
 >chmod 777 carpetaLocal
 2. Instalar en la máquina worker la librería **ffMPEg**. En una terminal ejecute:
 >sudo apt install ffmpeg
 3. Descargar el repositorio en ambas máquinas usando 
 >git clone https://github.com/jgutierrez9891/audioConverter.git
 4. Instalar la CLI de GCP usando los pasos de la siguiente guia: 
 >https://cloud.google.com/sdk/docs/install-sdk 
 5. Instalar el proxy de autenticación de Cloud SQL usando los pasos de la siguiente guia: 
 >https://cloud.google.com/sql/docs/postgres/quickstart-proxy-test
 6. Moverse a la carpeta del directorio en ambas máquinas. En una terminal ejecute:
 >cd audioConverter
 7. Instalar el entorno virtual de Python en ambas máquinas. En la terminal ejecute:
 >python3 -m venv env
 8. Active el entorno virtual de Python en ambas máquinas. En la terminal ejecute:
 >source env/bin/activate
 9. Instale las dependencias del proyecto en ambas máquinas. En la terminal ejecute:
 > python3 -m pip install -r requirements.txt
 10. En la máquina API abra una nueva terminal e inicie el API Flask. Ubiquese en la carpeta del proyecto que descargo de git (*audioConverter*) y ejecute los  siguientes comandos:
 > cd src
 >
 > flask run -p 3000
 11. En la máquina Worker abra una nueva terminal e inicie el convertidor Flask. Ejecute los siguientes comandos:
 >cd srcConverter
 >
 >flask run -p 5000
 12. En la máquina Worker abra una nueva terminal e inicie la cola. Ejecute los siguientes comandos:
 >cd src
 >
 >sudo docker run --rm -it -p 15672:15672 -p 5672:5672 rabbitmq:3-management
 13. En una nueva terminal inicie el componente de conexión a la cola para conversión. Ejecute los siguientes comandos:
 >cd src
 >
 >python3 consumer.py

***

## Iteración 2: API Escalado

[Release](https://github.com/jgutierrez9891/audioConverter/releases/tag/v1.2.0)

### Prerequisitos Cloud
Se deben cumplir los siguientes prerequisitos para el correcto funcionamiento de la solución:
1. Base de datos **Postgres** con un esquema llamado ***flask_db***, ejecutando en una instancia de base de datos del servicio cloud de SQL de GCP.
2. Bucket en **Cloud Storage** con carpeta y ruta para guardar tanto los archivos de subida como los archivos para descarga tanto originales como convertidos
3. 2 máquinas virtuales ambas con sistema operativo **Linux Debian 11.5**, una para el api y la otra para el worker
4. Tener git instalado en ambas máquinas
5. Configurar en la máquina del worker el Message broker **RabbitMQ** ejecutando y con una cola configurada así:
	 - Tipo: Clásica
	 - Nombre: ***conversion_processs***
	 - Durabilidad: Durable
	 - Auto borrado: NO
6. **Python 3.9** instalado en ambas máquinas
7. Realizar instalacion de Entorno virtual de Python en ambas máquinas. 
8. Para el API debe haber un script que ejecute Flask de manera automatica, para el worker en la línea de comandos ejecute:
>sudo apt-get install python3-venv
9. Balanceador de carga para generar nuevas máquinas de API deacuerdo a normas predefinidas

### Pasos para la instalación Cloud
 1. Instalar en la máquina worker la librería **ffMPEg**. En una terminal ejecute:
 >sudo apt install ffmpeg
 2. Descargar el repositorio en ambas máquinas usando 
 >git clone https://github.com/jgutierrez9891/audioConverter.git
 3. Instalar la CLI de GCP usando los pasos de la siguiente guia: 
 >https://cloud.google.com/sdk/docs/install-sdk 
 4. Moverse a la carpeta del directorio en ambas máquinas. En una terminal ejecute:
 >cd audioConverter
 5. Instalar el entorno virtual de Python en el worker. En la terminal ejecute:
 >python3 -m venv env
 6. Active el entorno virtual de Python en el worker. En la terminal ejecute:
 >source env/bin/activate
 7. Instale las dependencias del proyecto en el worker. En la terminal ejecute:
 > python3 -m pip install -r requirements.txt
 8. En la máquina Worker abra una nueva terminal e inicie el convertidor Flask. Ejecute los siguientes comandos:
 >cd srcConverter
 >
 >flask run -p 4000
 9. En la máquina Worker abra una nueva terminal e inicie la cola. Ejecute los siguientes comandos:
 >cd src
 >
 >sudo docker run --rm -it -p 15672:15672 -p 5672:5672 rabbitmq:3-management
 10. En una nueva terminal inicie el componente de conexión a la cola para conversión. Ejecute los siguientes comandos:
 >cd src
 >
 >python3 consumer.py
 11.  Una vez la máquina del API este configurada se debera generar una imagen a partir de esta para que sea usada como plantilla por un nuevo grupo de instancias
 12.  Crear un nuevo grupo de instancias con las siguientes configuraciones:
 		* Uso de la plantilla definida en el paso anterior
		* Ajuste de escala automático mínimo 1 y máximo 3
		* Métrica de autoescalado: uso del balanceo de carga al **80%**
		* Periodo de inactividad: **60 segundos**
		* Asignación de puertos: puerto **3000**
 13.   Crear un backend service que usa el grupo de instancias previamente creado
 14.   Crear un nuevo balanceador de carga que apunte al backend service previamente creado

***

## Iteración 3: Woker Escalado

[Release](https://github.com/jgutierrez9891/audioConverter/releases/tag/v1.3.0)

### Prerequisitos Cloud
Se deben cumplir los siguientes prerequisitos para el correcto funcionamiento de la solución:
1. Base de datos **Postgres** con un esquema llamado ***flask_db***, ejecutando en una instancia de base de datos del servicio cloud de SQL de GCP.
2. Bucket en **Cloud Storage** con carpeta y ruta para guardar tanto los archivos de subida como los archivos para descarga tanto originales como convertidos
3. 2 máquinas virtuales ambas con sistema operativo **Linux Debian 11.5**, una para el api y la otra para el worker
4. Tener git instalado en ambas máquinas
5. **Python 3.9** instalado en ambas máquinas
6. Realizar instalacion de Entorno virtual de Python en ambas máquinas. 
7. Para el API debe haber un script que ejecute Flask de manera automatica, para el worker en la línea de comandos ejecute:
>sudo apt-get install python3-venv

8. Balanceador de carga para generar nuevas máquinas de API deacuerdo a normas predefinidas
9.  Tema de **Cloud Pub/Sub** con nombre **ColaConverter**
10. Suscriptor al tema existente de **Cloud Pub/Sub** con nombre **SuscriptorWorker**

### Pasos para la instalación Cloud
 1. Instalar en la máquina worker la librería **ffMPEg**. En una terminal ejecute:
>sudo apt install ffmpeg
 2. Descargar el repositorio en ambas máquinas usando 
>git clone https://github.com/jgutierrez9891/audioConverter.git
 3. Instalar la CLI de GCP usando los pasos de la siguiente guia: 
>https://cloud.google.com/sdk/docs/install-sdk 
 4. Moverse a la carpeta del directorio en ambas máquinas. En una terminal ejecute:
>cd audioConverter
 5. Instalar el entorno virtual de Python en el worker. En la terminal ejecute:
>python3 -m venv env
 6. Active el entorno virtual de Python en el worker. En la terminal ejecute:
>source env/bin/activate
 7. Instale las dependencias del proyecto en el worker. En la terminal ejecute:
> python3 -m pip install -r requirements.txt
 8. En la máquina Worker abra una nueva terminal e inicie el convertidor Flask. Ejecute los siguientes comandos:
>cd srcConverter
>
>flask run -p 4000
 9.  En una nueva terminal inicie el componente de conexión a la cola para conversión. Ejecute los siguientes comandos:
> cd src
> 
> python3 consumer.py
 10.  Una vez la máquina del API este configurada se debera generar una imagen a partir de esta para que sea usada como plantilla por un nuevo grupo de instancias
 11.  Crear un nuevo grupo de instancias con las siguientes configuraciones:
 		* Uso de la plantilla definida en el paso anterior
		* Ajuste de escala automático mínimo 1 y máximo 3
		* Métrica de autoescalado: uso del balanceo de carga al **80%**
		* Periodo de inactividad: **60 segundos**
		* Asignación de puertos: puerto **3000**
 12.   Crear un backend service que usa el grupo de instancias previamente creado
 13.   Crear un nuevo balanceador de carga que apunte al backend service previamente creado
 14. Una vez la máquina del Worker este configurada se debera generar una imagen a partir de esta para que sea usada como plantilla por un nuevo grupo de instancias para el Worker
 15.  Crear un nuevo grupo de instancias con las siguientes configuraciones:
 		* Uso de la plantilla definida en el paso anterior
		* Ajuste de escala automático mínimo 1 y máximo 3
		* Métrica de autoescalado: Pub/Sub, **mensajes por VM 100**
		* Periodo de inactividad: **60 segundos**
		* Asignación de puertos: puerto **4000**


## Iteración 4: Aplicaciones desplegadas en GCP APP Engine

[Release](https://github.com/jgutierrez9891/audioConverter/releases/tag/v1.4.0)

### Prerequisitos Cloud
Se deben cumplir los siguientes prerequisitos para el correcto funcionamiento de la solución:
1. Base de datos **Postgres** con un esquema llamado ***flask_db***, ejecutando en una instancia de base de datos del servicio cloud de SQL de GCP.
2. Bucket en **Cloud Storage** con carpeta y ruta para guardar tanto los archivos de subida como los archivos para descarga tanto originales como convertidos
3. Crear un tema de **Cloud Pub/Sub** 
4. Suscriptor al tema existente de **Cloud Pub/Sub** con tipo de envío **Envio** 
5. Tener una cuenta de servicio **MailGun** con un dominio configurado

### Pasos para la instalación Cloud
Crear y desplegar una nueva aplicación de **App Engine**
 1. Acceda a **GCP Cloud Shell** 
 2. Configure una variable de entorno para su PROJECT_ID. Para ello, reemplace [YOUR_PROJECT_ID] por su propio ID del proyecto
>export PROJECT_ID=[YOUR_PROJECT_ID]
 3. Defina el proyecto con el comando
>gcloud config set project ${PROJECT_ID}
 4. Cree una cuenta de servicio para acceder a las API de Google Cloud
>gcloud iam service-accounts create converter --display-name "Converter Service Account"
 5. Otorgue los permisos adecuados a su nueva cuenta de servicio
>gcloud projects add-iam-policy-binding $ {PROJECT_ID} --member serviceAccount:codelab@${PROJECT_ID}.iam.gserviceaccount.com --role roles/owner
 6. Después de crear su cuenta de servicio, cree una clave para ella
>gcloud iam service-accounts keys create ~/key.json \
--iam-account codelab@${PROJECT_ID}.iam.gserviceaccount.com

Este comando genera una clave de cuenta de servicio que se almacena en un archivo JSON llamado key.json en su directorio principal

 7. Descargue el repositorio usando 
>git clone https://github.com/jgutierrez9891/audioConverter.git
 8. Ubíquese a la carpeta del directorio en ambas máquinas. En una terminal ejecute:
>cd audioConverter
 9.  Edite el archivo en la ruta **src/app.yaml** para actualizar los valores correspondientes a las variables:
    	* CLOUD_STORAGE_BUCKET:[BUCKET_NAME] - Nombre del bucket creado como prerequisito
    	* PUBSUB_TOPIC:[TOPIC_NAME] - Nombre del tema de Pub/Sub creado como prerequisito
    	* GOOGLE_APPLICATION_CREDENTIALS: [CREDENTIALS_JSON_FILE] - Nombre del archivo json de credenciales creado en el paso 6
    	* service_account: [ID_SERVICE_ACCOUNT] - Identificador de la cuenta de servicio creada en el paso 4
 10. Copie el archivo de credenciales creado en el paso 6 en el directorio src
>cp /home/[USER]/[CREDENTIALS_JSON_FILE] src/
 11. Edite el archivo en la ruta **srcConverter/app_cola.yaml** para actualizar los valores correspondientes a las variables:
    	* CLOUD_STORAGE_BUCKET:[BUCKET_NAME] - Nombre del bucket creado como prerequisito
    	* PUBSUB_TOPIC:[TOPIC_NAME] - Nombre del tema de Pub/Sub creado como prerequisito
    	* GOOGLE_APPLICATION_CREDENTIALS: [CREDENTIALS_JSON_FILE] - Nombre del archivo json de credenciales creado en el paso 6
    	* service_account: [ID_SERVICE_ACCOUNT] - Identificador de la cuenta de servicio creada en el paso 4
    	* EMAIL_API_KEY: [API_KEY_MAIL_GUN] - API key del servicio de correo de mailgun
    	* PUBSUB_VERIFICATION_TOKEN: [SOME_STRING] - Cadena aleatoria para comprobar los mensajes recibidos desde Pub/Sub
 12. Copie el archivo de credenciales creado en el paso 6 en el directorio srcConverter
>cp /home/[USER]/[CREDENTIALS_JSON_FILE] srcConverter/
 13. Cree la aplicación de **App Engine**
>gcloud app create
 14. Despliegue los servicios de la app
>gcloud app deploy src/app.yaml srcConverter/app_cola.yaml
 15. Una vez finalizado el proceso de despliegue, revise en la consola de GCP en el servicio App Engine los servicios y versiones creadas
 16. Copie la URL generada para la aplicación de **APP Engine**
 17. Actualice la configuración de la suscripción de Pub/Sub para definer la **Enviar URL de extremo** como **urlBaseAppEngine:8081/api/listenerMessage?token=[PUBSUB_VERIFICATION_TOKEN]** reemplanzando [PUBSUB_VERIFICATION_TOKEN] con el valor definido en el archivo **srcConverter/app_cola.yaml**
