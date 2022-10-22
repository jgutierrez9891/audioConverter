import json
from unittest import TestCase

from faker import Faker
from faker.generator import random

from srcConverter.app import app
from srcConverter.modelos.modelos import User, db


