import traceback
from flask import request
from flask_restful import Resource
from pydub import AudioSegment
from srcConverter.modelos.modelos import User, db, Task
import requests
from datetime import datetime
import os
from google.cloud import storage

storage_client = storage.Client()

def upload_to_bucket(blob_name, file_path):
    try:
        bucket = storage_client.get_bucket('audioconverter-files')
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        # blob.upload_from_file()
        return True
    except Exception as e:
        print(e)
        return False

def download_from_bucket(blob_name, file_path):
    try:
        bucket = storage_client.get_bucket('audioconverter-files')
        blob = bucket.blob(blob_name)
        with open(file_path, 'wb') as f:
            storage_client.download_blob_to_file(blob, f)
        return True
    except Exception as e:
        print(e)
        return False
class Converter(Resource):
    def post(self):
        
        print('storage preparing')
        storage_client = storage.Client()
        audio_bucket = storage_client.get_bucket('audioconverter-files')
        print('bucket name')
        print(audio_bucket.name)

        print('storage test started')
        blobname= 'english.pdf'
        filepath = os.path.join(os.getcwd(), 'file2.pdf')
        download_from_bucket(blobname, filepath)
        
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
        postR = False
        try:
            if format == "mp3":
                song = AudioSegment.from_mp3(location)
                song.export(locationNoFormat+"."+nFormat, format=nFormat)
                if postR:
                    x = requests.post(url = url,auth = auth ,data = jsons)
                    print(x)
                taskTmp.status = "processed"
                db.session.commit()
                print("converted to mp3")
                return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
            elif format == "ogg":
                song = AudioSegment.from_ogg(location)
                song.export(locationNoFormat+"."+nFormat, format=nFormat)
                if postR:
                    x = requests.post(url = url,auth = auth ,data = jsons)
                    print(x)
                taskTmp.status = "processed"
                db.session.commit()
                print("converted to ogg")
                return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
            elif format == "wav":
                song = AudioSegment.from_wav(location)
                song.export(locationNoFormat+"."+nFormat, format=nFormat)
                if postR:
                    x = requests.post(url = url,auth = auth ,data = jsons)
                    print(x)
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
            