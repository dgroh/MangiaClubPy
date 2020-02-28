from flask import Flask, make_response, request
from flask_restful import Resource, reqparse
from datetime import datetime, timedelta
from functools import wraps
from bson import ObjectId
import jwt
import json
import bcrypt
import uuid
import os

from . import HttpStatusCode
from db import mongo, redis

token_audience = ''  # TODO: What is the audience?
token_issuer = ''  # TODO: What is the issuer?


def token_required(f):
    @wraps(f)
    def decorated(self, *args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return make_response('[HTTP_403_FORBIDDEN]', HttpStatusCode.HTTP_403_FORBIDDEN)

        try:
            data = jwt.decode(token, os.getenv(
                'SECRET_KEY'), audience=token_audience, issuer=token_issuer, algorithms=['HS256'])

            claim_sub = data['sub']
            claim_email = data['email']

            user = mongo.db.users.find_one(
                {'_id': ObjectId(claim_sub), 'email': claim_email})

            if not user:
                return make_response('[INVALID_TOKEN]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)

            user_id = str(user['_id'])

            token_alive = redis.get(user_id)

            if not token_alive:
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

        users = mongo.db.users

        user = users.find_one_or_404({'email': args['email']})

        if bcrypt.checkpw(args['password'].encode('utf-8'), user['hashed_password']):
            try:
                user_id = str(user['_id'])

                expires_in = timedelta(days=60)

                payload = {
                    'iss': token_issuer,
                    'aud': token_audience,
                    'exp': datetime.utcnow() + expires_in,
                    'iat': datetime.utcnow(),
                    'sub': user_id,
                    'email': user['email'],
                    'jti:': str(uuid.uuid4())
                }

                token = jwt.encode(payload, os.getenv(
                    'SECRET_KEY'), algorithm='HS256').decode('utf-8')

                redis.setex(user_id, int(expires_in.total_seconds()), token)

                return make_response({'token': token}, HttpStatusCode.HTTP_201_CREATED)
            except Exception as e:
                # TODO: Log the exception
                return make_response('[HTTP_500_INTERNAL_SERVER_ERROR]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)

        return make_response('[HTTP_401_UNAUTHORIZED]', HttpStatusCode.HTTP_401_UNAUTHORIZED)


class Logout(Resource):

    @token_required
    def delete(self, user_id):
        redis.delete(user_id)

        return '[HTTP_204_NO_CONTENT]', HttpStatusCode.HTTP_204_NO_CONTENT
