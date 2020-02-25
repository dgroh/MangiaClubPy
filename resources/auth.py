from flask import Flask, make_response
from flask_restful import Resource, reqparse
from datetime import datetime, timedelta
import os
import bcrypt
import jwt

from . import HttpStatusCode
from db import mongo

parser = reqparse.RequestParser()
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)

class Login(Resource):
    def __init__(self):
        pass

    def post(self):
        args = parser.parse_args()

        users = mongo.db.users

        user = users.find_one_or_404({'email': args['email']})

        if bcrypt.checkpw(args['password'].encode('utf-8'), user['hashed_password']):
            try:
                payload = {
                    'exp': datetime.utcnow() + timedelta(days=1),
                    'iat': datetime.utcnow(),
                    'sub': str(user['_id'])
                }
                
                token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256').decode("utf-8")

                return make_response({'token': token}, HttpStatusCode.HTTP_201_CREATED)
            except Exception as e:
                # TODO: Log the exception 
                return '[HTTP_500_INTERNAL_SERVER_ERROR]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR

        return '[HTTP_401_UNAUTHORIZED]', HttpStatusCode.HTTP_401_UNAUTHORIZED