# -*- coding: utf-8 -*-
""" Event module which holds all the logic for handling events.

Currently the event is represented by the arguments of the HTTP request, which are:

- Name - [Required]
- Start datetime - [Required]
- End datetime - [Required]
- Max guests allowed - [Required]
- Cuisine - [Required]
- Price per person - [Request]
- Description - [Request]
- Guests - [Not Required and only available for `put`]
- Rating - [Not Required and only available for `put`]

"""

from flask import make_response, current_app as app
from flask_restful import Resource, reqparse
from datetime import datetime
from bson import ObjectId

from api.resources.constants import HttpStatusCode
from api.resources.auth import token_required

base_parser = reqparse.RequestParser()
base_parser.add_argument('name', required=True, location='json')
base_parser.add_argument('start_datetime', required=True, location='json')
base_parser.add_argument('end_datetime', required=True, location='json')
base_parser.add_argument('max_guests_allowed', required=True, type=int, location='json')
base_parser.add_argument('cuisine', required=True, action='append', location='json')
base_parser.add_argument('price_per_person', required=True, type=float, location='json')
base_parser.add_argument('description', required=True, location='json')


class Event(Resource):

    def __init__(self):
        """
        This class represents the event resource.
        
        Here also a copy of the request parser is made and all 
        arguments are set as not required as for `get` and `put`
        required arguments are not needed. 

        The request parser is extended for `put` with following arguments: 
        - `guests`
        - `rating`
        """

        self.parser = base_parser.copy()

        # TODO: Use list comprehension with new symbol in Python 3.8: 
        # https://stackoverflow.com/questions/10291997/how-can-i-do-assignments-in-a-list-comprehension
        for arg in self.parser.args:
            arg.required = False

        self.parser.add_argument('guests', action='append', location='json')
        self.parser.add_argument('rating', location='json')

    def get(self, id):
        """
        This method returns the event found by id.
        
        __Returns:__

        * If id is invalid: A json response with the text [HTTP_400_BAD_REQUEST]
        * If event not found: A json response with the text [HTTP_404_NOT_FOUND]
        * If success: A json response with the event data
        """

        if not ObjectId.is_valid(id):
            return make_response('[HTTP_400_BAD_REQUEST]', HttpStatusCode.HTTP_400_BAD_REQUEST)

        object_id = ObjectId(id)

        event = app.mongo.db.events.find_one({'_id': object_id})

        if not event:
            return make_response('[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

        event['_id'] = str(event['_id'])

        return make_response({'data': event}, HttpStatusCode.HTTP_200_OK)

    @token_required
    def put(self, user_id, id):
        """
        This method updates the event and is only accessible with authentication token.
        
        __Returns:__

        * If id is invalid: A json response with the text [HTTP_400_BAD_REQUEST]
        * If event not found: A json response with the text [HTTP_404_NOT_FOUND]
        * If success: No content as per default for HTTP Status Code 204
        """

        if not ObjectId.is_valid(id):
            return make_response('[HTTP_400_BAD_REQUEST]', HttpStatusCode.HTTP_400_BAD_REQUEST)

        args = self.parser.parse_args()

        object_id = ObjectId(id)

        events = app.mongo.db.events

        event = app.mongo.db.events.find_one({'_id': object_id})

        if not event:
            return make_response('[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

        fields = {key: value for key,
                  value in args.items() if value is not None}

        events.update_one({'_id': object_id},
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


class EventList(Resource):
    """
    This class represents events resource.
    """

    def get(self):
        """
        This method returns the list of events.
        
        __Returns:__

        A json response with list of events or an empty list if no events in the database
        """

        response = []
        events = app.mongo.db.events.find()

        for event in events:
            event['_id'] = str(event['_id'])
            response.append(event)

        return make_response({'data': response}, HttpStatusCode.HTTP_200_OK)

    @token_required
    def post(self, user_id):
        """
        This method creates a new event.
        
        __Returns:__

        * If success: A json response with the text [HTTP_201_CREATED]
        """

        args = base_parser.parse_args()

        events = app.mongo.db.events

        events.insert_one({
            'host_id': user_id,
            'name': args['name'],
            'start_datetime': args['start_datetime'],
            'end_datetime': args['end_datetime'],
            'max_guests_allowed': args['max_guests_allowed'],
            'cuisine': args['cuisine'],
            'price_per_person': args['price_per_person'],
            'description': args['description'],
            'published:': True,
            'view_count:': 0,
            'created_by_user': user_id,
            'created_datetime': datetime.utcnow()
        })

        return make_response('[HTTP_201_CREATED]', HttpStatusCode.HTTP_201_CREATED)
