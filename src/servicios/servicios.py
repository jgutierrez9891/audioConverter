from ast import Not
import os
import re
import traceback
from flask import request, jsonify, send_file
from datetime import datetime
from flask_restful import Resource
from modelos.modelos import User, db, Task
from werkzeug.utils import secure_filename
from utilities.utilities import allowed_file
from flask import current_app as app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from publisher import publish_messages
from pydub import AudioSegment
from sqlalchemy.sql import text
from google.cloud import storage

storage_client = storage.Client()

def validate_email(email):
        pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        if re.match(pattern,email):
            return True
        return False

def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )

    return password_ok

def serialize(row):
    return {
        "id" : str(row.id),
        "fileName" : row.fileName,
        "newFormat" : row.newFormat,
        "status" : row.status
    } 

def download_from_bucket(blob_name, file_path_destiny):
    try:
        bucket = storage_client.get_bucket('audioconverter-files')
        blob = bucket.blob(blob_name)
        with open(file_path_destiny, 'wb') as f:
            storage_client.download_blob_to_file(blob, f)
        return True
    except Exception as e:
        print(e)
        return False

class Tasks(Resource):
    
    @jwt_required()
    def get(self):
        # current_user_id = request.json['id_usuario'] #for testing without JWT
        current_user_id = get_jwt_identity()
        args = request.args
        try:
            order = int(args.get("order"))
        except:
            order =0

        try:
            maxel = int(args.get("maxel"))
        except:
            maxel =0

        if maxel>0:
            if order==0:
                tasksList = Task.query.filter_by(id_usuario=current_user_id).order_by(text('id')).limit(maxel).all()
            else:
                tasksList = Task.query.filter_by(id_usuario=current_user_id).order_by(text('id desc')).limit(maxel).all()
        else:
            if order==0:
                tasksList = Task.query.filter_by(id_usuario=current_user_id).order_by(text('id')).all()
            else:
                tasksList = Task.query.filter_by(id_usuario=current_user_id).order_by(text('id desc')).all()

        tasksResp =[serialize(x) for x in tasksList]
        return jsonify({'tasks': tasksResp})

    @jwt_required()
    def post(self):
        now = datetime.now()
        dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
        # id_usuario = request.values['id_usuario'] #for testing without JWT
        id_usuario = get_jwt_identity()
        if 'nombreArchivo' not in request.files:
            return {"resultado": "ERROR", "mensaje": "La petición no contiene el archivo"}, 410
        file = request.files["nombreArchivo"]
        if file.filename == '':
            return {"resultado": "ERROR", "mensaje": 'Debe seleccionar un archivo de audio para ser convertido'}, 411
        if file and allowed_file(file.filename):
            #ct = datetime.now()
            #currentMilliseconds = str(ct.timestamp()).replace(".","")
            
            filename = secure_filename(file.filename)
            #dirname = os.path.dirname(os.path.abspath(__file__))
            #file.save(os.path.join(dirname, "/"+currentMilliseconds+filename))
            
            storage_client = storage.Client()
            audio_bucket = storage_client.get_bucket(app.config['GCP_BUCKET_NAME'])
            
            #filepath = dirname + "/" + currentMilliseconds+filename
            blob = audio_bucket.blob(filename)
            blob.upload_from_file(file)

            #os.remove(filepath)
        else:
            print ("Formato invalido" + file.filename)
            return {"resultado": "ERROR", "mensaje": 'Ingrese un formato de archivo válido'}, 412
        usuario = User.query.get(id_usuario)
        if usuario is None:
            return {"resultado": "ERROR", "mensaje": 'El id de usuario ingresado no existe'}, 409
        nueva_tarea = Task(fileName = filename, newFormat = request.values['nuevoFormato'], \
            timeStamp = dt_string, status = "uploaded", id_usuario = id_usuario)
        db.session.add(nueva_tarea)
        db.session.commit()

        #Se envía tarea a la cola
        mensaje = {"filepath":str(filename), "newFormat":request.values['nuevoFormato'], "id": nueva_tarea.id}
        q = publish_messages(mensaje)
        return {"mensaje": "Tarea creada exitosamente", "id": nueva_tarea.id}
    
class TaskR(Resource):

    @jwt_required()
    def get(self, taskId):
        taskTmp = Task.query.filter(Task.id == taskId).first()
        if(taskTmp is not None):
            return {"id": taskTmp.id,
                    "fileName" : taskTmp.fileName,
                    "newFormat" : taskTmp.newFormat,
                    "timeStamp" : taskTmp.timeStamp.strftime('%m/%d/%Y'),
                    "status" : taskTmp.status}
        else:
            return {"resultado": "ERROR", "mensaje": "No se encontro la tarea"}, 400
    
    @jwt_required()
    def put(self, taskId):
        # id_usuario = request.values['id_usuario'] #for testing without JWT
        id_usuario = get_jwt_identity()
        usuario = User.query.get(id_usuario)

        if usuario is None:
            return {"resultado": "ERROR", "mensaje": 'El id de usuario ingresado no existe'}, 409

        tarea = Task.query.filter(Task.id == taskId and Task.id_usuario==id_usuario).first()
        destinationFormat = tarea.newFormat
        justFileName = tarea.fileName.split('.')[0]
        destinationFileName = justFileName+"."+destinationFormat
        if tarea.status =="processed":
            if(os.path.isfile(destinationFileName)):
                os.remove(destinationFileName)
        tarea.newFormat = request.values["nuevoFormato"]
        tarea.status = "uploaded"

        db.session.commit()
        #Se envía tarea a la cola
        mensaje = {"filepath":tarea.fileName, "newFormat":request.values['nuevoFormato'], "id": tarea.id}
        q = publish_messages(mensaje)
        return {"mensaje": "Tarea actualizada exitosamente", "tarea": serialize(tarea)},200
    
    @jwt_required()
    def delete(self, taskId):
        task = Task.query.get_or_404(taskId)
        justFileName = task.fileName.split('.')[0]
        destinationFormat = task.newFormat
        destinationFileName = justFileName+"."+destinationFormat

        if(os.path.isfile(destinationFileName)):
            os.remove(destinationFileName)
        db.session.delete(task)
        db.session.commit()
        return {"mensaje": "Tarea eliminada exitosamente", "id": taskId},200

class Auth(Resource):    
    def post(self):
        try:
            email = request.json["email"]
        except KeyError as e:
            return {"resultado": "ERROR", "mensaje": "Debe proporcionar un correo electrónico"}, 400

        try:
            email = request.json["username"]
        except KeyError as e:
            return {"resultado": "ERROR", "mensaje": "Debe proporcionar un nombre de usuario"}, 400

        try:
            email = request.json["password1"]
        except KeyError as e:
            return {"resultado": "ERROR", "mensaje": "Debe proporcionar una contraseña"}, 400

        try:
            email = request.json["password2"]
        except KeyError as e:
            return {"resultado": "ERROR", "mensaje": "Debe proporcionar la confirmación de la contraseña"}, 400
        
        if(validate_email(request.json["email"]) != True):
            return {"resultado": "ERROR", "mensaje": "El correo electrónico suministrado no es válido"}, 400

        if request.json["password1"] != request.json["password2"]:
            return {"resultado": "ERROR", "mensaje": "La clave de confirmación no coincide"}, 400

        if(password_check(request.json["password1"]) != True):
            return {"resultado": "ERROR", "mensaje": "La clave suministrada no cumple criterios mínimos. Por favor suministre una clave \n1%"+
        "con las siguientes características: \n1%"+
        "8 o más caracteres \n1%"+
        "1 o más dígitos \n1%"+
        "1 o más símbolos \n1%"+
        "1 o más letras mayúsculas \n1%"+
        "1 o más letras minúsculas"}, 400

        userTmpUsername = User.query.filter(User.username == request.json["username"]).first()
        if(userTmpUsername is not None):
            return {"resultado": "ERROR", "mensaje": "El usuario seleccionado ya existe"}, 400

        userTmpEmail = User.query.filter(User.email == request.json["email"]).first()
        if(userTmpEmail is not None):
            return {"resultado": "ERROR", "mensaje": "El correo electrónico suministrado ya existe"}, 400
        
        nuevoUsuario = User(username = request.json["username"], email = request.json["email"], password=request.json["password1"])
        db.session.add(nuevoUsuario)
        db.session.commit()
        return {"resultado": "OK", "mensaje": "Usuario creado exitosamente"}, 200
    
    
class Health(Resource):    
    def get(self):
        return {"resultado": "OK", "mensaje": "service is alive"}, 200
    

class AuthLogin(Resource):    
    def post(self):
        try:
            username = request.json["username"]
        except KeyError as e:
            return {"resultado": "ERROR", "mensaje": "Debe proporcionar un nombre de usuario"}, 400

        try:
            password = request.json["password"]
        except KeyError as e:
            return {"resultado": "ERROR", "mensaje": "Debe proporcionar una contraseña"}, 400

        user = User.query.filter(User.username == request.json["username"], User.password == request.json["password"]).first()
        if(user is None):
            return {"resultado": "ERROR", "mensaje": "Credenciales inválidas"}, 403

        token_de_acceso = create_access_token(identity=user.id)
        return {"resultado": "OK", "mensaje": "Inicio de sesión exitoso", "token": token_de_acceso}, 200

class FilesR(Resource):   
    @jwt_required()
    def get(self, filename):
        storage_client = storage.Client()
        audio_bucket = storage_client.get_bucket(app.config['GCP_BUCKET_NAME'])

        filepath = str(app.config['UPLOAD_FOLDER'])+"/"+filename
        blob = str(filepath)[1:]
        local_filepath = str(app.config['UPLOAD_FOLDER'])+"/"+filename
        file_downloaded = download_from_bucket(blob, local_filepath)

        try:
            return send_file(local_filepath, attachment_filename=filename)
        except:
            return {"resultado": "ERROR", "mensaje": 'El archivo no existe'}, 409
    
    
