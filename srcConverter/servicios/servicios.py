import base64
import json
import traceback
from flask import request
from flask import current_app as app
from flask_restful import Resource
from pydub import AudioSegment
from modelos.modelos import User, db, Task
import requests
from datetime import datetime
import os
from google.cloud import storage

storage_client = storage.Client()

def download_from_bucket(blob_name, file_path_destiny):
    try:
        bucket = storage_client.get_bucket(app.config['GCP_BUCKET_NAME'])
        blob = bucket.blob(blob_name)
        with open(file_path_destiny, 'wb') as f:
            storage_client.download_blob_to_file(blob, f)
        return True
    except Exception as e:
        print(e)
        return False

def convert(request):
    print('storage preparing')
    storage_client = storage.Client()
    audio_bucket = storage_client.get_bucket(app.config['GCP_BUCKET_NAME'])
    print('bucket name')
    print(audio_bucket.name)

    print("coverter started")

    now = datetime.now()
    url = "https://api.mailgun.net/v3/sandboxddf98cda1dd84031bc13cda246e42344.mailgun.org/messages"
    auth = ("api", app.config['EMAIL_API_KEY'])

    taskTmp = Task.query.filter(Task.id == int(request.json["id"])).first()
    taskTmp.conversionTimeStamp = now.strftime("%Y-%m-%d %H:%M:%S")
    db.session.commit()
    print("commit 1 done")
    taskTmp.secondsTakedToStartConversion = (taskTmp.conversionTimeStamp  - taskTmp.timeStamp).total_seconds()
    db.session.commit()
    print("commit 2 done")
    
    userTmp = User.query.filter(User.id == taskTmp.id_usuario).first()
    
    local_filepath = "/tmp/"+request.json["filepath"]
    bucket_filepath = request.json["filepath"]
    download_from_bucket(bucket_filepath, local_filepath)
    nFormat = request.json["newFormat"]
    
    locationNoFormat = bucket_filepath.split(".")[0]
    format = bucket_filepath.split(".")[1]
    
    jsons = {"from": "mbkane04@gmail.com",
                "to": [userTmp.email],
                "subject": "Your file Conversion is done!",
                "text": "The File: "+str(bucket_filepath)+" has been converted"}
    
    print("before convert")
    postR = False
    try:
        destinyPath = '/tmp/'+ locationNoFormat+"."+nFormat
        if format == "mp3":
            song = AudioSegment.from_mp3(local_filepath)
            song.export(destinyPath, format=nFormat)
            bucket = storage_client.get_bucket(app.config['GCP_BUCKET_NAME'])
            blob = bucket.blob(destinyPath[5:])
            blob.upload_from_filename(destinyPath)
            if postR:
                x = requests.post(url = url,auth = auth ,data = jsons)
                print(x)
            taskTmp.status = "processed"
            db.session.commit()
            print("converted to " + nFormat)
            os.remove(local_filepath)
            os.remove(destinyPath)
            return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
        elif format == "ogg":
            song = AudioSegment.from_ogg(local_filepath)
            song.export(destinyPath, format=nFormat)
            bucket = storage_client.get_bucket(app.config['GCP_BUCKET_NAME'])
            blob = bucket.blob(destinyPath[5:])
            blob.upload_from_filename(destinyPath)
            if postR:
                x = requests.post(url = url,auth = auth ,data = jsons)
                print(x)
            taskTmp.status = "processed"
            db.session.commit()
            print("converted to " + nFormat)
            os.remove(local_filepath)
            os.remove(destinyPath)
            return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
        elif format == "wav":
            song = AudioSegment.from_wav(local_filepath)
            song.export(destinyPath, format=nFormat)
            bucket = storage_client.get_bucket(app.config['GCP_BUCKET_NAME'])
            blob = bucket.blob(destinyPath[5:])
            blob.upload_from_filename(destinyPath)
            if postR:
                x = requests.post(url = url,auth = auth ,data = jsons)
                print(x)
            taskTmp.status = "processed"
            db.session.commit()
            print("converted to " + nFormat)
            os.remove(local_filepath)
            os.remove(destinyPath)
            return {"mensaje": "Se Realizo la conversion exitosamente"}, 200
        else:
            print("incorrect format return")
            os.remove(local_filepath)
            return {"resultado": "ERROR", "mensaje": "El formato no se reconoce"}, 400       
    except Exception: 
        print("error in conversion !!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(traceback.print_exc())
        taskTmp = Task.query.filter(Task.id == int(request.json["id"])).first()
        db.session.commit()
        os.remove(local_filepath)
        return {"resultado": "ERROR", "mensaje": traceback.print_exc()}, 400
    print("Done")


class MessageListener(Resource):
    def post(self):
        envelope = json.loads(request.data.decode('utf-8'))
        payload = base64.b64decode(envelope['message']['data'])

        bodyAsJson = json.loads(payload)
        return convert(bodyAsJson)