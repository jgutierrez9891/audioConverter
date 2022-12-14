import json
from unittest import TestCase

from faker import Faker
from faker.generator import random

from src.app import app
from src.modelos.modelos import User, db


class TestAuth(TestCase):
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

    def test_succes_signup(self):
        password = "MyPassword2022*"
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.email(),
            "password1": password,
            "password2": password
        }

        signup_request = self.client.post("/api/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 200)

    def test_error_signup_existing_user(self):
        new_user2 = {
            "username": self.new_user["username"],
            "email": self.data_factory.email(),
            "password1": self.password,
            "password2": self.password
        }

        signup_request2 = self.client.post("/api/auth/signup",
                                                   data=json.dumps(new_user2),
                                                   headers={'Content-Type': 'application/json'})

        signup_response2 = json.loads(signup_request2.get_data())

        self.assertEqual(signup_request2.status_code, 400)
        self.assertEqual(signup_response2["mensaje"], "El usuario seleccionado ya existe")

    def test_error_signup_existing_email(self):
        new_user2 = {
            "username": self.data_factory.name(),
            "email": self.new_user["email"],
            "password1": self.password,
            "password2": self.password
        }

        signup_request2 = self.client.post("/api/auth/signup",
                                                   data=json.dumps(new_user2),
                                                   headers={'Content-Type': 'application/json'})

        signup_response2 = json.loads(signup_request2.get_data())

        self.assertEqual(signup_request2.status_code, 400)
        self.assertEqual(signup_response2["mensaje"], "El correo electr??nico suministrado ya existe")

    def test_error_signup_confirmation_password(self):
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.email(),
            "password1": "MyPassword2022*",
            "password2": "MyPassword2023*"
        }

        signup_request = self.client.post("/api/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 400)
        signup_response = json.loads(signup_request.get_data())

        self.assertEqual(signup_response["mensaje"], "La clave de confirmaci??n no coincide")
    
    def test_error_signup_invalid_email(self):
        password = "MyPassword2022*"
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.name(),
            "password1": password,
            "password2": password
        }

        signup_request = self.client.post("/api/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 400)
        signup_response = json.loads(signup_request.get_data())

        self.assertEqual(signup_response["mensaje"], "El correo electr??nico suministrado no es v??lido")
    
    def test_error_signup_weak_password(self):
        password = self.data_factory.word()
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.email(),
            "password1": password,
            "password2": password
        }

        signup_request = self.client.post("/api/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 400)
        signup_response = json.loads(signup_request.get_data())

        self.assertEqual(signup_response["mensaje"], "La clave suministrada no cumple criterios m??nimos. Por favor suministre una clave \n1%"+
        "con las siguientes caracter??sticas: \n1%"+
        "8 o m??s caracteres \n1%"+
        "1 o m??s d??gitos \n1%"+
        "1 o m??s s??mbolos \n1%"+
        "1 o m??s letras may??sculas \n1%"+
        "1 o m??s letras min??sculas")

    def test_error_signup_no_username(self):
        password = "MyPassword2022*"
        new_user = {
            "email": self.data_factory.email(),
            "password1": password,
            "password2": password
        }

        signup_request = self.client.post("/api/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 400)
        signup_response = json.loads(signup_request.get_data())

        self.assertEqual(signup_response["mensaje"], "Debe proporcionar un nombre de usuario")

    

    def test_succes_login(self):
        login_data = {
            "username": self.new_user["username"],
            "password": self.password,
        }

        login_request = self.client.post("/api/auth/login",
                                                   data=json.dumps(login_data),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(login_request.status_code, 200)
        login_response = json.loads(login_request.get_data())

        self.assertIsNotNone(login_response["token"])
    
    def test_error_login(self):
        login_data = {
            "username": self.data_factory.name(),
            "password": self.data_factory.word(),
        }

        login_request = self.client.post("/api/auth/login",
                                                   data=json.dumps(login_data),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(login_request.status_code, 403)
    
    def test_error_no_password(self):
        login_data = {
            "username": self.data_factory.name()
        }

        login_request = self.client.post("/api/auth/login",
                                                   data=json.dumps(login_data),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(login_request.status_code, 400)
        login_response = json.loads(login_request.get_data())

        self.assertEqual(login_response["mensaje"], "Debe proporcionar una contrase??a")
    
    def test_error_no_username(self):
        login_data = {
            "password": self.data_factory.name()
        }

        login_request = self.client.post("/api/auth/login",
                                                   data=json.dumps(login_data),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(login_request.status_code, 400)
        login_response = json.loads(login_request.get_data())

        self.assertEqual(login_response["mensaje"], "Debe proporcionar un nombre de usuario")

    def tearDown(self) -> None:
        users = User.query.all()
        for item in users:
            try:
                db.session.delete(item)
                db.session.commit()
            except Exception:
                db.session.rollback()
                return 'Error deleting user: '+item
        return super().tearDown()