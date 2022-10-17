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

class Auth(Resource):    
    def post(self):
        if(validate_email(request.json["email"]) != True):
            return {"resultado": "ERROR", "mensaje": "El correo electrónico suministrado no es válido"}, 400

        if request.json["password1"] != request.json["password2"]:
            return {"resultado": "ERROR", "mensaje": "La clave de confirmación no coincide"}, 400

        if(password_check(request.json["password1"]) != True):
            return {"resultado": "ERROR", "mensaje": "La clave suministrada no cumple criterios mínimos. Por favor suministre una clave \n1%"+
        "con las siguientes características: \n1%"+
        "8 o más caracteres \n1%"+
        "1 o más digitos \n1%"+
        "1 o más simbolos \n1%"+
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