import traceback
from flask import request
from flask_restful import Resource
from pydub import AudioSegment
from srcConverter.modelos.modelos import User, db, Task
import requests
from datetime import datetime


class Converter(Resource):
    def post(self):
        print("coverter started")
        now = datetime.now()
        url = "https://api.mailgun.net/v3/sandboxddf98cda1dd84031bc13cda246e42344.mailgun.org/messages"
        auth = ("api", "API_KEY")

        taskTmp = Task.query.filter(Task.id == int(request.json["id"])).first()
        taskTmp.conversionTimeStamp = now.strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()
        print("commit 1 done")
        taskTmp.secondsTakedToStartConversion = (taskTmp.conversionTimeStamp  - taskTmp.timeStamp).total_seconds()
        db.session.commit()
        print("commit 2 done")
        
        userTmp = User.query.filter(User.id == taskTmp.id_usuario).first()
        
        location = request.json["filepath"]
        nFormat = request.json["newFormat"]
        
        locationNoFormat = location.split(".")[0]
        format = location.split(".")[1]
        
        jsons = {"from": "mbkane04@gmail.com",
                 "to": [userTmp.email],
			     "subject": "Your file Conversion is done!",
			     "text": "The File: "+str(location)+" has been converted"}
        
        print("before convert")
        try:
            if format == "mp3":
                song = AudioSegment.from_mp3(location)
                song.export(locationNoFormat+"."+nFormat, format=nFormat)
                #x = requests.post(url = url,auth = auth ,data = jsons)
                #print(x)
                taskTmp.status = "processed"
                db.session.commit()
                print("converted to mp3")
                return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
            else: 
                if format == "ogg":
                    song = AudioSegment.from_ogg(location)
                    song.export(locationNoFormat+"."+nFormat, format=nFormat)
                    #x = requests.post(url = url,auth = auth ,data = jsons)
                    #print(x)
                    taskTmp.status = "processed"
                    db.session.commit()
                    print("converted to ogg")
                    return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
                else:
                    if format == "wav":
                        song = AudioSegment.from_wav(location)
                        song.export(locationNoFormat+"."+nFormat, format=nFormat)
                        #x = requests.post(url = url,auth = auth ,data = jsons)
                        #print(x)
                        taskTmp.status = "processed"
                        db.session.commit()
                        print("converted to wav")
                        return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
                    else:
                        print("incorrect format return")
                        return {"resultado": "ERROR", "mensaje": "El formato no se reconoce"}, 400
        except Exception: 
            print("error")
            print(traceback.print_exc())
            taskTmp = Task.query.filter(Task.id == int(request.json["id"])).first()
            taskTmp.conversionTimeStamp = ""
            taskTmp.secondsTakedToStartConversion = ""
            db.session.commit()
            return {"resultado": "ERROR", "mensaje": traceback.print_exc()}, 400
            