from flask import Flask, make_response
from flask_restful import Resource, reqparse
import bcrypt

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
            return make_response({'token': ''}, HttpStatusCode.HTTP_201_CREATED)

        return '[HTTP_401_UNAUTHORIZED]', HttpStatusCode.HTTP_401_UNAUTHORIZED