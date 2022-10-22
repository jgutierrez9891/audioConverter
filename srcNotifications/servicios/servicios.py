from ast import Not
import os
import re
import traceback
from flask import request
from flask_restful import Resource
import yagmail
    
class sendEmail(Resource):
    def post(self):
        try:
            yag = yagmail.SMTP("audioconverternotify@gmail.com","xykqcyzummcgdxbm")
            contents = [
                "The task id "+str(request.json["idTask"])+" has been peformed" 
            ]
            yag.send('d.chala@uniandes.edu.co', 'Notification Task # '+str(request.json["idTask"]), contents)
            return {"mensaje": "Se Envio el mensaje correctamente"}, 200
        except Exception: 
            {"resultado": "ERROR", "mensaje": traceback.print_exc()}, 400
            