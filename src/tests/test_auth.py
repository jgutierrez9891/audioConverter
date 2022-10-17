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

    def test_succes_signup(self):
        password = "MyPassword2022*"
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.email(),
            "password1": password,
            "password2": password
        }

        signup_request = self.client.post("/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 200)

    def test_error_signup_existing_user(self):
        password = "MyPassword2022*"
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.email(),
            "password1": password,
            "password2": password
        }

        signup_request = self.client.post("/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 200)

        new_user2 = {
            "username": new_user["username"],
            "email": self.data_factory.email(),
            "password1": password,
            "password2": password
        }

        signup_request2 = self.client.post("/auth/signup",
                                                   data=json.dumps(new_user2),
                                                   headers={'Content-Type': 'application/json'})

        signup_response2 = json.loads(signup_request2.get_data())

        self.assertEqual(signup_request2.status_code, 400)
        self.assertEquals(signup_response2["mensaje"], "El usuario seleccionado ya existe")

    def test_error_signup_existing_email(self):
        password = "MyPassword2022*"
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.email(),
            "password1": password,
            "password2": password
        }

        signup_request = self.client.post("/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 200)

        new_user2 = {
            "username": self.data_factory.name(),
            "email": new_user["email"],
            "password1": password,
            "password2": password
        }

        signup_request2 = self.client.post("/auth/signup",
                                                   data=json.dumps(new_user2),
                                                   headers={'Content-Type': 'application/json'})

        signup_response2 = json.loads(signup_request2.get_data())

        self.assertEqual(signup_request2.status_code, 400)
        self.assertEquals(signup_response2["mensaje"], "El correo electrónico suministrado ya existe")

    def test_error_signup_confirmation_password(self):
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.email(),
            "password1": "MyPassword2022*",
            "password2": "MyPassword2023*"
        }

        signup_request = self.client.post("/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 400)
        signup_response = json.loads(signup_request.get_data())

        self.assertEquals(signup_response["mensaje"], "La clave de confirmación no coincide")
    
    def test_error_signup_invalid_email(self):
        password = "MyPassword2022*"
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.name(),
            "password1": password,
            "password2": password
        }

        signup_request = self.client.post("/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 400)
        signup_response = json.loads(signup_request.get_data())

        self.assertEquals(signup_response["mensaje"], "El correo electrónico suministrado no es válido")
    
    def test_error_signup_weak_password(self):
        password = self.data_factory.word()
        new_user = {
            "username": self.data_factory.name(),
            "email": self.data_factory.email(),
            "password1": password,
            "password2": password
        }

        signup_request = self.client.post("/auth/signup",
                                                   data=json.dumps(new_user),
                                                   headers={'Content-Type': 'application/json'})

        self.assertEqual(signup_request.status_code, 400)
        signup_response = json.loads(signup_request.get_data())

        self.assertEquals(signup_response["mensaje"], "La clave suministrada no cumple criterios mínimos. Por favor suministre una clave \n1%"+
        "con las siguientes características: \n1%"+
        "8 o más caracteres \n1%"+
        "1 o más dígitos \n1%"+
        "1 o más símbolos \n1%"+
        "1 o más letras mayúsculas \n1%"+
        "1 o más letras minúsculas")


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