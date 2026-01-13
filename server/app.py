#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        bio = data.get('bio', "")
        image_url = data.get('image_url', "")

        if not username or not password:
            return {"errors": ["Username and password required"]}, 422

        try:
            user = User(username=username, bio=bio, image_url=image_url)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return {
                "id": user.id,
                "username": user.username,
                "bio": user.bio,
                "image_url": user.image_url
            }, 201
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username must be unique"]}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"errors": ["Not logged in"]}, 401
        user = User.query.get(user_id)
        if not user:
            return {"errors": ["Not logged in"]}, 401
        return {
            "id": user.id,
            "username": user.username,
            "bio": user.bio,
            "image_url": user.image_url
        }, 200

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not user.authenticate(password):
            return {"errors": ["Invalid username or password"]}, 401
        
        session['user_id'] = user.id
        return {
            "id": user.id,
            "username": user.username,
            "bio": user.bio,
            "image_url": user.image_url
        }, 200

class Logout(Resource):
    def delete(self):
        if not session.get('user_id'):
            return {"errors": ["Not logged in"]}, 401
        session.pop('user_id')
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"errors": ["Not logged in"]}, 401
        recipes = Recipe.query.all()
        result = []
        for r in recipes:
            result.append({
                "id": r.id,
                "title": r.title,
                "instructions": r.instructions,
                "minutes_to_complete": r.minutes_to_complete,
                "user": {
                    "id": r.user.id,
                    "username": r.user.username,
                    "bio": r.user.bio,
                    "image_url": r.user.image_url
                }
            })
        return result, 200
    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"errors": ["Not logged in"]}, 401
        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username,
                    "bio": recipe.user.bio,
                    "image_url": recipe.user.image_url
                }
            }, 201
        except (IntegrityError, ValueError) as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5000, debug=True)