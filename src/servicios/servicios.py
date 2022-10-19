from ast import Not
import os
import re
from flask import request
from datetime import datetime
from flask_restful import Resource
from src.modelos.modelos import User, db, Task
from werkzeug.utils import secure_filename
from src.utilities.utilities import allowed_file
from flask import current_app as app
from flask_jwt_extended import create_access_token, jwt_required

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

class Tasks(Resource):
    def post(self):
        now = datetime.now()
        dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
        if 'nombreArchivo' not in request.files:
            return 'La petición no contiene el archivo', 410
        file = request.files["nombreArchivo"]
        if file.filename == '':
            return 'Debe seleccionar un archivo de audio para ser convertido', 411
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = app.config['UPLOAD_FOLDER'] + "\\" + filename
        print("El nombre del archivo es" + filename)
        nueva_tarea = Task(fileName = filepath, newFormat = request.values['nuevoFormato'], \
            timeStamp = dt_string, status = "uploaded")
        db.session.add(nueva_tarea)
        db.session.commit()
        return {"mensaje": "Tarea creada exitosamente", "id": nueva_tarea.id}
    
class TaskR(Resource):
    def get(self, userid):
        print("userid: "+userid)
        taskTmp = Task.query.filter(Task.id == userid).first()
        if(taskTmp is not None):
            return {"id": taskTmp.id,
                    "fileName" : taskTmp.fileName,
                    "newFormat" : taskTmp.newFormat,
                    "timeStamp" : taskTmp.timeStamp.strftime('%m/%d/%Y'),
                    "status" : taskTmp.status}
        else:
            return {"resultado": "ERROR", "mensaje": "No se encontro la tarea"}, 400

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