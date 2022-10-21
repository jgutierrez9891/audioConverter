from ast import Not
import os
import re
import traceback
from flask import request
from datetime import datetime
from flask_restful import Resource
from srcConverter.modelos.modelos import User, db, Task
from werkzeug.utils import secure_filename
from src.utilities.utilities import allowed_file
from flask import current_app as app
from flask_jwt_extended import create_access_token, jwt_required
from pydub import AudioSegment

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
    
class Converter(Resource):
    def post(self):
        
        print("location: "+request.json["location"])
        location = request.json["location"]
    
        print("newFormat: "+request.json["nFormat"])
        nFormat = request.json["nFormat"]
        
        print("locationNoFormat: "+location.split(".")[0])
        locationNoFormat = location.split(".")[0]
        
        print("format: "+location.split(".")[1])
        format = location.split(".")[1]
        
        try:
            print(locationNoFormat+"."+nFormat)
            if format == "mp3":
                song = AudioSegment.from_mp3(location)
                song.export(locationNoFormat+"."+nFormat, format=nFormat)
                return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
            else: 
                if format == "ogg":
                    song = AudioSegment.from_ogg(location)
                    song.export(locationNoFormat+"."+nFormat, format=nFormat)
                    return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
                else:
                    if format == "wav":
                        song = AudioSegment.from_wav(location)
                        song.export(locationNoFormat+"."+nFormat, format=nFormat)
                        return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
                    else:
                        return {"resultado": "ERROR", "mensaje": "El formato no se reconoce"}, 400
        except Exception: 
            {"resultado": "ERROR", "mensaje": traceback.print_exc()}, 400
            