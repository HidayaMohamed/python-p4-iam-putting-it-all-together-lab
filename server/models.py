from sqlalchemy.orm import validates,relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column("password_hash", db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationship: One User has many Recipes
    recipes = relationship("Recipe", back_populates="user", cascade="all, delete-orphan", passive_deletes=False)

    # Password property setter/getter
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password is not readable!")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    # Optional: Validate username presence
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username must be present")
        return username

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False, default=60)

    # Relationship: Recipe belongs to a User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship("User", back_populates="recipes")

    # Validation for instructions length
    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions or len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long")
        return instructions
    
    # Validation for title presence
    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title must be present")
        return title

    # Validation for minutes_to_complete
    @validates('minutes_to_complete')
    def validate_minutes(self, key, minutes):
        if minutes is None:
            raise ValueError("minutes_to_complete must be present")
        return minutes