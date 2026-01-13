import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe

class TestRecipe:
    '''User in models.py'''

   