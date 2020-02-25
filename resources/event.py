from datetime import datetime
from flask import Flask, make_response
from flask_restful import Resource, reqparse
from bson import ObjectId

from . import HttpStatusCode
from db import mongo

base_parser = reqparse.RequestParser()
base_parser.add_argument('name', required=True, location='json')
base_parser.add_argument('start_date_time', required=True, location='json')
base_parser.add_argument('end_date_time', required=True, location='json')
base_parser.add_argument('max_guests_allowed', required=True, type=int, location='json')
base_parser.add_argument('cuisine', required=True, action='append', location='json')
base_parser.add_argument('price_per_person', required=True, type=float, location='json')
base_parser.add_argument('description', required=True, location='json')

class Event(Resource):
    def __init__(self):
        self.parser = base_parser.copy()

        for arg in self.parser.args:
            arg.required=False

        self.parser.add_argument('guests', action='append', location='json')
        self.parser.add_argument('rating', location='json')

    def get(self, id):
        object_id = ObjectId(id)

        event = mongo.db.events.find_one_or_404({'_id': object_id})

        event['_id'] = str(event['_id'])

        return make_response({'data': event}, HttpStatusCode.HTTP_200_OK)

    def put(self, id):
        args = self.parser.parse_args()

        object_id = ObjectId(id)

        events = mongo.db.events

        events.find_one_or_404({'_id': object_id})

        fields = {key: value for key,value in args.items() if value is not None}

        events.update_one({'_id': object_id},
        {
            '$push': {
                '_changes': {
                    '_fields': fields,
                    '_updated_by_user': '',
                    '_updated_date_time': datetime.utcnow()
                }
            }
        })

        return '[HTTP_204_NO_CONTENT]', HttpStatusCode.HTTP_204_NO_CONTENT


class EventList(Resource):
    def __init__(self):
        self.parser = base_parser.copy()

    def get(self):
        response = []
        events = mongo.db.events.find()

        for event in events:
            event['_id'] = str(event['_id'])
            response.append(event)

        return make_response({'data': response}, HttpStatusCode.HTTP_200_OK)

    def post(self):
        args = self.parser.parse_args()

        events = mongo.db.events

        events.insert_one({
            'host_id': '',
            'name': args['name'],
            'start_date_time': args['start_date_time'],
            'end_date_time': args['end_date_time'],
            'max_guests_allowed': args['max_guests_allowed'],
            'cuisine': args['cuisine'],
            'price_per_person': args['price_per_person'],
            'description': args['description'],
            'published:': True,
            '_view_count:': 0,
            '_created_by_user': '',
            '_created_date_time': datetime.utcnow()
        })

        return '[HTTP_201_CREATED]', HttpStatusCode.HTTP_201_CREATED
