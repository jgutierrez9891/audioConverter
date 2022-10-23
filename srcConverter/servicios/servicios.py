import traceback
from flask import request
from flask_restful import Resource
from pydub import AudioSegment
from srcConverter.modelos.modelos import User, db, Task
import requests
from datetime import datetime


class Converter(Resource):
    def post(self):
        
        now = datetime.now()
        url = "http://127.0.0.1:4000/api/notify"
        
        taskTmp = Task.query.filter(Task.id == int(request.json["id"])).first()
        taskTmp.conversionTimeStamp = now.strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()
        
        print((taskTmp.conversionTimeStamp  - taskTmp.timeStamp).total_seconds())
        taskTmp.secondsTakedToStartConversion = (taskTmp.conversionTimeStamp  - taskTmp.timeStamp).total_seconds()
        db.session.commit()
        
        userTmp = User.query.filter(User.id == taskTmp.id_usuario).first()
        
        jsons = {"email":userTmp.email,"file":request.json["filepath"]}
        
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
                x = requests.post(url = url, json = jsons)
                print(x)
                taskTmp.status = "converted"
                db.session.commit()
                return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
            else: 
                if format == "ogg":
                    song = AudioSegment.from_ogg(location)
                    song.export(locationNoFormat+"."+nFormat, format=nFormat)
                    x = requests.post(url = url, json = jsons)
                    print(x)
                    taskTmp.status = "converted"
                    db.session.commit()
                    return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
                else:
                    if format == "wav":
                        song = AudioSegment.from_wav(location)
                        song.export(locationNoFormat+"."+nFormat, format=nFormat)
                        x = requests.post(url = url, json = jsons)
                        print(x)
                        taskTmp.status = "converted"
                        db.session.commit()
                        return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
                    else:
                        return {"resultado": "ERROR", "mensaje": "El formato no se reconoce"}, 400
        except Exception: 
            taskTmp = Task.query.filter(Task.id == int(request.json["id"])).first()
            taskTmp.conversionTimeStamp = ""
            taskTmp.secondsTakedToStartConversion = ""
            db.session.commit()
            return {"resultado": "ERROR", "mensaje": traceback.print_exc()}, 400
            