from flask import Flask, make_response, request
from flask_restful import Resource, reqparse
from datetime import datetime, timedelta
from functools import wraps
import os
import bcrypt
import jwt

from . import HttpStatusCode
from db import mongo

def token_required(f):
    @wraps(f)
    def decorated(self, *args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return make_response('[HTTP_403_FORBIDDEN]', HttpStatusCode.HTTP_403_FORBIDDEN)         

        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'))
        except Exception as e:
            # TODO: Log the exception 
            return make_response('[INVALID_TOKEN]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)         

        return f(self, data['sub'], *args, **kwargs)

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
                payload = {
                    'exp': datetime.utcnow() + timedelta(days=1),
                    'iat': datetime.utcnow(),
                    'sub': str(user['_id'])
                }
                
                token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')

                return make_response({'token': token.decode("utf-8")}, HttpStatusCode.HTTP_201_CREATED)
            except Exception as e:
                # TODO: Log the exception 
                return make_response('[HTTP_500_INTERNAL_SERVER_ERROR]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)         

        return make_response('[HTTP_401_UNAUTHORIZED]', HttpStatusCode.HTTP_401_UNAUTHORIZED) 