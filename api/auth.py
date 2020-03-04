from flask import make_response, request, current_app as app
from flask_restful import Resource, reqparse
from datetime import datetime, timedelta
from functools import wraps
from bson import ObjectId
import jwt
import bcrypt

from .constants import HttpStatusCode


def token_required(f):
    @wraps(f)
    def decorated(self, *args, **kwargs):
        token = None

        if 'Access-Token' in request.headers:
            token = request.headers['Access-Token']

        if not token:
            return make_response('[HTTP_403_FORBIDDEN]', HttpStatusCode.HTTP_403_FORBIDDEN)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

            claim_sub = data['sub']
            claim_email = data['email']

            token_alive = app.redis.get(claim_sub)

            if not token_alive:
                return make_response('[INVALID_TOKEN]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)

            user_id = claim_sub.replace('auth|', '')

            user = app.mongo.db.users.find_one({'_id': ObjectId(user_id), 'email': claim_email})

            if not user:
                return make_response('[INVALID_TOKEN]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # TODO: Log the exception
            return make_response('[INVALID_TOKEN]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)

        return f(self, user_id, *args, **kwargs)

    return decorated


class Login(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', required=True)
        self.parser.add_argument('password', required=True)

    def post(self):
        args = self.parser.parse_args()
        email = args['email']
        password = args['password']

        users = app.mongo.db.users

        user = users.find_one({'email': email})

        if not user:
            return make_response('[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

        if bcrypt.checkpw(password.encode('utf-8'), user['hashed_password']):
            try:
                expires_in = timedelta(days=60)

                user_id = str(user['_id'])

                payload = {
                    'exp': datetime.utcnow() + expires_in,
                    'iat': datetime.utcnow(),
                    'sub': f'auth|{user_id}',
                    'email': email,
                    'phone:': user['phone']
                }

                token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

                app.redis.setex(payload['sub'], int(expires_in.total_seconds()), token)

                return make_response({'token': token}, HttpStatusCode.HTTP_201_CREATED)
            except Exception as e:
                # TODO: Log the exception
                return make_response('[HTTP_500_INTERNAL_SERVER_ERROR]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)

        return make_response('[HTTP_401_UNAUTHORIZED]', HttpStatusCode.HTTP_401_UNAUTHORIZED)


class Logout(Resource):

    @token_required
    def delete(self, user_id):
        app.redis.delete(f'auth|{user_id}')

        return '[HTTP_204_NO_CONTENT]', HttpStatusCode.HTTP_204_NO_CONTENT
