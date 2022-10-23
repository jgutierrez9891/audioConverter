import json
from unittest import TestCase
from faker import Faker
from srcConverter.app import app



class TestAuth(TestCase):
    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        
    def test_task_convert(self):
        self.mailData = {
            "email":"daachalabu@unal.edu.co",
            "file":"E:\\flor.mp3"
        }
        signup_request = self.client.post("/api/notify",data=json.dumps(self.mailData), headers={'Content-Type': 'application/json'})
        self.assertEqual(signup_request.status_code, 200)
        
    def tearDown(self) -> None:
        return super().tearDown()