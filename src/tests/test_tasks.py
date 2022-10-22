import json
from unittest import TestCase
from faker import Faker
from faker.generator import random

from src.app import app
from src.modelos.modelos import User, Task, db

class TestTasks(TestCase):
    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()

        self.password = "MyPassword2022*"
        self.new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.email(),
            "password1": self.password,
            "password2": self.password
        }

        signup_request = self.client.post("/api/auth/signup",
                                                   data=json.dumps(self.new_user),
                                                   headers={'Content-Type': 'application/json'})

    def test_create_task_without_file(self):
        login_data = {
            "username": self.new_user["username"],
            "password": self.password,
        }

        login_request = self.client.post("/api/auth/login",
                                                   data=json.dumps(login_data),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(login_request.status_code, 200)
        login_response = json.loads(login_request.get_data())

        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(login_response["token"])}
        
        data = {"nuevoFormato": "mp3", "id_usuario" : "1"}
        solicitud_nueva_tarea = self.client.post("/api/tasks", data = data, 
                            headers = headers, content_type='multipart/form-data')

        self.assertEqual(solicitud_nueva_tarea.status_code, 410)

        error_al_crear_tarea = json.loads(solicitud_nueva_tarea.get_data())
        self.assertEqual(error_al_crear_tarea['mensaje'],"La petición no contiene el archivo")

    def test_create_task(self):
        login_data = {
            "username": self.new_user["username"],
            "password": self.password,
        }

        login_request = self.client.post("/api/auth/login",
                                                   data=json.dumps(login_data),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(login_request.status_code, 200)
        login_response = json.loads(login_request.get_data())

        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(login_response["token"])}
        
        data = {"nuevoFormato": "mp3", "id_usuario" : "1"}
        data['nombreArchivo'] = open('resources\David Guetta - Titanium.mp3' ,'rb')
        solicitud_nueva_tarea = self.client.post("/api/tasks", data = data, 
                            headers = headers, content_type='multipart/form-data')

        self.assertEqual(solicitud_nueva_tarea.status_code, 200)
        tarea_creada = json.loads(solicitud_nueva_tarea.get_data())
        self.assertEqual(tarea_creada["mensaje"],"Tarea creada exitosamente")

    def test_create_task_invalid_format(self):
        login_data = {
            "username": self.new_user["username"],
            "password": self.password,
        }

        login_request = self.client.post("/api/auth/login",
                                                   data=json.dumps(login_data),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(login_request.status_code, 200)
        login_response = json.loads(login_request.get_data())

        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(login_response["token"])}
        
        data = {"nuevoFormato": "mp3", "id_usuario" : "1"}
        data['nombreArchivo'] = open('resources\Archivo_texto.txt' ,'rb')
        solicitud_nueva_tarea = self.client.post("/api/tasks", data = data, 
                            headers = headers, content_type='multipart/form-data')

        self.assertEqual(solicitud_nueva_tarea.status_code, 412)
        tarea_creada = json.loads(solicitud_nueva_tarea.get_data())
        self.assertEqual(tarea_creada["mensaje"],"Ingrese un formato de archivo válido")
    
    def test_delete_task(self):
        login_data = {
            "username": self.new_user["username"],
            "password": self.password,
        }

        login_request = self.client.post("/api/auth/login",
                                                   data=json.dumps(login_data),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(login_request.status_code, 200)
        login_response = json.loads(login_request.get_data())

        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(login_response["token"])}
        
        data = {"nuevoFormato": "mp3"}
        data['nombreArchivo'] = open('resources\David Guetta - Titanium.mp3' ,'rb')
        solicitud_nueva_tarea = self.client.post("/api/tasks", data = data, 
                            headers = headers, content_type='multipart/form-data')

        self.assertEqual(solicitud_nueva_tarea.status_code, 200)
        tarea_creada = json.loads(solicitud_nueva_tarea.get_data())
        self.assertEqual(tarea_creada["mensaje"],"Tarea creada exitosamente")

        idTarea = tarea_creada["id"]
        solicitud_eliminar_tarea = self.client.delete("/api/tasks/"+str(idTarea),  
                            headers = headers, content_type='multipart/form-data')
        self.assertEqual(solicitud_eliminar_tarea.status_code, 200)

    def tearDown(self) -> None:
        users = User.query.all()
        for item in users:
            try:
                db.session.delete(item)
                db.session.commit()
            except Exception:
                db.session.rollback()
                return 'Error deleting user: '+item
        tasks = Task.query.all()
        for item in tasks:
            try:
                db.session.delete(item)
                db.session.commit()
            except Exception:
                db.session.rollback()
                return 'Error deleting task: '+item
        return super().tearDown()


        


