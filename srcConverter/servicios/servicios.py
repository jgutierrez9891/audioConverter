import traceback
from flask import request
from flask_restful import Resource
from pydub import AudioSegment
import requests


class Converter(Resource):
    def post(self):
        
        url = "http://127.0.0.1:4000/api/notify"
        
        json = {"idTask":request.json["id"]}
        
        print("location: "+request.json["filepath"])
        location = request.json["filepath"]
    
        print("newFormat: "+request.json["newFormat"])
        nFormat = request.json["newFormat"]
        
        locationNoFormat = location.split(".")[0]
        
        format = location.split(".")[1]
        
        try:
            if format == "mp3":
                song = AudioSegment.from_mp3(location)
                song.export(locationNoFormat+"."+nFormat, format=nFormat)
                x = requests.post(url = url, json = json)
                print(x)
                return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
            else: 
                if format == "ogg":
                    song = AudioSegment.from_ogg(location)
                    song.export(locationNoFormat+"."+nFormat, format=nFormat)
                    x = requests.post(url = url, json = json)
                    return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
                else:
                    if format == "wav":
                        song = AudioSegment.from_wav(location)
                        song.export(locationNoFormat+"."+nFormat, format=nFormat)
                        x = requests.post(url = url, json = json)
                        return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
                    else:
                        return {"resultado": "ERROR", "mensaje": "El formato no se reconoce"}, 400
        except Exception: 
            {"resultado": "ERROR", "mensaje": traceback.print_exc()}, 400
            