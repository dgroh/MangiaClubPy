from datetime import datetime
from flask import Flask, jsonify
from flask_restful import Resource, reqparse
from db import mongo
from bson import ObjectId
import json
import bcrypt

parser = reqparse.RequestParser()
parser.add_argument('email', location='json')
parser.add_argument('first_name', location='json')
parser.add_argument('last_name', location='json')
parser.add_argument('password', location='json')
parser.add_argument('phone', location='json')
parser.add_argument('is_host', type=bool, location='json')
parser.add_argument('rating', location='json')

class User(Resource):
    def get(self, user_id):
        object_id = ObjectId(user_id)

        user = mongo.db.users.find_one_or_404({ '_id': object_id })

        user['_id'] = str(user['_id'])
        user['password'] = str(user['password'])
        user['password_salt'] = str(user['password_salt'])

        return jsonify({'data': user})

    def put(self, user_id):
        object_id = ObjectId(user_id)

        users = mongo.db.users

        users.find_one_or_404({ '_id': object_id })

        args = parser.parse_args()

        fields = { key: value for key,value in args.items() if value is not None }

        users.update_one({ '_id': object_id },
        {
            '$push': {
                '_changes': {
                    '_fields': fields,
                    '_updated_by_user': '',
                    '_updated_date_time': datetime.utcnow()
                }
            }
        })

        return '', 204


class UserList(Resource):
    def get(self):
        response = []
        users = mongo.db.users.find()

        for user in users:
            user['_id'] = str(user['_id'])
            user['password'] = str(user['password'])
            user['password_salt'] = str(user['password_salt'])
            response.append(user)

        return jsonify({'data': response})

    def post(self):
        args = parser.parse_args()

        existing_user = mongo.db.users.find_one({ 'email': args['email'] })

        if existing_user is None:
            password_salt = bcrypt.gensalt()
            hash_pass = bcrypt.hashpw(args['password'].encode('utf-8'), password_salt)

            mongo.db.users.insert_one({
                'email': args['email'],
                'first_name': args['first_name'],
                'last_name': args['last_name'],
                'password': hash_pass,
                'password_salt': password_salt,
                'phone': args['phone'],
                'published:': True,
                '_view_count:': 0,
                '_created_by_user': args['email'],
                '_created_date_time': datetime.utcnow()
            })

            return '', 201

        return '', 409
