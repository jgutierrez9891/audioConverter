import os
from flask import request
from datetime import datetime
from flask_restful import Resource
from src.modelos.modelos import db, Task
from werkzeug.utils import secure_filename
from src.utilities.utilities import allowed_file
from flask import current_app as app

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

    
