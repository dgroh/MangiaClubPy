# -*- coding: utf-8 -*-
""" User module which holds all the logic of the application user.

Currently the user is represented by the arguments of the HTTP request, which are:

- Email - [Required]
- First name - [Required]
- Last name - [Required]
- Password - [Required]
- Phone number - [Required]
- Is Host - [Not Required and only available for `put`]
- Rating - [Not Required and only available for `put`]

"""

from flask import make_response, current_app as app
from flask_restful import Resource, reqparse
from datetime import datetime
from bson import ObjectId
import bcrypt

from api.resources.constants import HttpStatusCode
from api.resources.auth import token_required


base_parser = reqparse.RequestParser()
base_parser.add_argument('email', required=True, location='json')
base_parser.add_argument('first_name', required=True, location='json')
base_parser.add_argument('last_name', required=True, location='json')
base_parser.add_argument('password', required=True, location='json')
base_parser.add_argument('phone', required=True, location='json')


class User(Resource):
    """
    """

    def __init__(self):
        """
        This class represents the user resource.
        
        Here also a copy of the request parser is made and all 
        arguments are set as not required as for `get` and `put`
        required arguments are not needed. 

        The request parser is extended for `put` with following arguments: 
        - `is_host`
        - `rating`
        """

        self.parser = base_parser.copy()

        for arg in self.parser.args:
            arg.required = False

        self.parser.add_argument('is_host', type=bool, location='json')
        self.parser.add_argument('rating', location='json')

    def get(self, id):
        """
        This method returns the user found by id.
        
        __Returns:__

        * If id is invalid: A json response with the text [HTTP_400_BAD_REQUEST]
        * If user not found: A json response with the text [HTTP_404_NOT_FOUND]
        * If success: A json response with the user data
        """

        if not ObjectId.is_valid(id):
            return make_response('[HTTP_400_BAD_REQUEST]', HttpStatusCode.HTTP_400_BAD_REQUEST)

        object_id = ObjectId(id)

        user = app.mongo.db.users.find_one({'_id': object_id})

        if not user:
            return make_response('[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

        user['_id'] = str(user['_id'])
        user['hashed_password'] = user['hashed_password'].decode('utf-8')
        user['password_salt'] = user['password_salt'].decode('utf-8')

        return make_response({'data': user}, HttpStatusCode.HTTP_200_OK)

    @token_required
    def put(self, user_id, id):
        """
        This method updates the user and is only accessible with authentication token.
        
        __Returns:__

        * If id is invalid: A json response with the text [HTTP_400_BAD_REQUEST]
        * If user not found: A json response with the text [HTTP_404_NOT_FOUND]
        * If success: No content as per default for HTTP Status Code 204
        """

        if not ObjectId.is_valid(id):
            return make_response('[HTTP_400_BAD_REQUEST]', HttpStatusCode.HTTP_400_BAD_REQUEST)

        args = self.parser.parse_args()

        object_id = ObjectId(id)

        users = app.mongo.db.users

        user = app.mongo.db.users.find_one({'_id': object_id})

        if not user:
            return make_response('[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

        fields = {key: value for key,
                  value in args.items() if value is not None}

        # The update occurs only if arguments have been passed via request
        if len(fields):
            users.update_one({'_id': object_id},
                            {
                '$push': {
                    'changes': {
                        'fields': fields,
                        'updated_by_user': user_id,
                        'updated_datetime': datetime.utcnow()
                    }
                }
            })

        return '[HTTP_204_NO_CONTENT]', HttpStatusCode.HTTP_204_NO_CONTENT


class UserList(Resource):
    """
    This class represents users resource.
    """

    def get(self):
        """
        This method returns the list of users.
        
        __Returns:__

        A json response with list of users or an empty list if no users in the database
        """

        response = []
        users = app.mongo.db.users.find()

        for user in users:
            user['_id'] = str(user['_id'])
            user['hashed_password'] = user['hashed_password'].decode('utf-8')
            user['password_salt'] = user['password_salt'].decode('utf-8')

            response.append(user)

        return make_response({'data': response}, HttpStatusCode.HTTP_200_OK)

    def post(self):
        """
        This method creates a new user.
        
        __Returns:__

        * If user already exists: A json response with the text [HTTP_409_CONFLICT]
        * If success: A json response with the text [HTTP_201_CREATED]
        """

        args = base_parser.parse_args()

        email = args['email'].strip()

        existing_user = app.mongo.db.users.find_one({'email': email})

        if existing_user is None:
            password_salt = bcrypt.gensalt()

            hashed_password = bcrypt.hashpw(args['password'].strip().encode('utf-8'), password_salt)

            inserted_id = app.mongo.db.users.insert_one({
                'email': email,
                'first_name': args['first_name'].strip(),
                'last_name': args['last_name'].strip(),
                'hashed_password': hashed_password,
                'password_salt': password_salt,
                'phone': args['phone'].strip(),
                'published:': True,
                'created_datetime': datetime.utcnow()
            }).inserted_id

            app.mongo.db.users.update_one({'_id': inserted_id},
                                      {
                '$set': {
                    'created_by_user': str(inserted_id)
                }
            })

            return make_response('[HTTP_201_CREATED]', HttpStatusCode.HTTP_201_CREATED)

        return make_response('[HTTP_409_CONFLICT]', HttpStatusCode.HTTP_409_CONFLICT)
