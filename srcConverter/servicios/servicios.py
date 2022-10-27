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
        url = "https://api.mailgun.net/v3/sandboxd586480a798c4b9098cfe10b39e3a060.mailgun.org/messages"
        auth = ("api", "458a382568a1d6f5ae4bf6051fbcbaf0-8845d1b1-fa254d35")
        
        taskTmp = Task.query.filter(Task.id == int(request.json["id"])).first()
        taskTmp.conversionTimeStamp = now.strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()
        
        #print((taskTmp.conversionTimeStamp  - taskTmp.timeStamp).total_seconds())
        taskTmp.secondsTakedToStartConversion = (taskTmp.conversionTimeStamp  - taskTmp.timeStamp).total_seconds()
        db.session.commit()
        
        userTmp = User.query.filter(User.id == taskTmp.id_usuario).first()
        
        #print("location: "+request.json["filepath"])
        location = request.json["filepath"]
    
        #print("newFormat: "+request.json["newFormat"])
        nFormat = request.json["newFormat"]
        
        locationNoFormat = location.split(".")[0]
        
        format = location.split(".")[1]
        
        print(userTmp.email)
        
        jsons = {"from": "mbkane04@gmail.com",
                 "to": [userTmp.email],
			     "subject": "Your file Conversion is done!",
			     "text": "The File: "+str(location)+" has been converted"}
        
        try:
            if format == "mp3":
                song = AudioSegment.from_mp3(location)
                song.export(locationNoFormat+"."+nFormat, format=nFormat)
                x = requests.post(url = url,auth = auth ,data = jsons)
                print(x)
                taskTmp.status = "processed"
                db.session.commit()
                return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
            else: 
                if format == "ogg":
                    song = AudioSegment.from_ogg(location)
                    song.export(locationNoFormat+"."+nFormat, format=nFormat)
                    #x = requests.post(url = url, json = jsons)
                    #print(x)
                    taskTmp.status = "processed"
                    db.session.commit()
                    return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
                else:
                    if format == "wav":
                        song = AudioSegment.from_wav(location)
                        song.export(locationNoFormat+"."+nFormat, format=nFormat)
                        x = requests.post(url = url, json = jsons)
                        #print(x)
                        taskTmp.status = "processed"
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
            