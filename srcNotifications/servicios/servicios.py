import traceback
from flask import request
from flask_restful import Resource
import yagmail
    
class sendEmail(Resource):
    def post(self):
        try:
            yag = yagmail.SMTP("audioconverternotify@gmail.com","xykqcyzummcgdxbm")
            contents = [
                "The File: "+str(request.json["file"])+" has been converted" 
            ]
            yag.send(request.json["email"], 'Your file Conversion is done!', contents)
            return {"mensaje": "Se Envio el mensaje correctamente"}, 200
        except Exception: 
            {"resultado": "ERROR", "mensaje": traceback.print_exc()}, 400
            