from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


# ----------------------------
# SIGNUP
# ----------------------------
class Signup(Resource):
    def post(self):
        data = request.get_json()

        try:
            user = User(
                username=data.get('username'),
                image_url=data.get('image_url'),
                bio=data.get('bio'),
            )
            user.password_hash = data.get('password')

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 201

        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422


# ----------------------------
# CHECK SESSION
# ----------------------------
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.get(user_id)
            if user:
                return {
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                }, 200

        return {"error": "Unauthorized"}, 401


# ----------------------------
# LOGIN
# ----------------------------
class Login(Resource):
    def post(self):
        data = request.get_json()

        user = User.query.filter_by(
            username=data.get('username')
        ).first()

        if user and user.authenticate(data.get('password')):
            session['user_id'] = user.id

            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 200

        return {"error": "Invalid username or password"}, 401


# ----------------------------
# LOGOUT
# ----------------------------
class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return {}, 204

        return {"error": "Unauthorized"}, 401


# ----------------------------
# RECIPES
# ----------------------------
class RecipeIndex(Resource):

    def get(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()

        return [
            {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username,
                    "image_url": recipe.user.image_url,
                    "bio": recipe.user.bio
                }
            }
            for recipe in recipes
        ], 200

    def post(self):
        user_id = session.get('user_id')

        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        try:
            recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete'),
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
                    "image_url": recipe.user.image_url,
                    "bio": recipe.user.bio
                }
            }, 201

        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422


api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)