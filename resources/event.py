from datetime import datetime
from flask import Flask
from flask_restful import Resource, reqparse
from .extensions import mongo_client
from bson import ObjectId
import json

parser = reqparse.RequestParser()
parser.add_argument('name', location='json')
parser.add_argument('start_date_time', help="Start date and time musst be a valid datetime", location='json')
parser.add_argument('end_date_time', help="End date and time musst be a valid datetime", location='json')
parser.add_argument('max_guests_allowed', type=int, location='json')
parser.add_argument('cuisine', action='append', location='json')
parser.add_argument('price_per_person', type=int, location='json')
parser.add_argument('description', location='json')
parser.add_argument('guests', action='append', location='json')
parser.add_argument('rating', location='json')

# shows a single event item and lets you delete or update an event
class Event(Resource):
    def get(self, event_id):
        object_id = ObjectId(event_id)

        response = json.dumps(mongo_client.db.events.find_one_or_404({ '_id': object_id }), default=str)

        return { 'response': response }

    def put(self, event_id):
        object_id = ObjectId(event_id)

        mongo_client.db.events.find_one_or_404({ '_id': object_id })

        args = parser.parse_args()

        fields = { key: value for key,value in args.items() if value is not None }

        mongo_client.db.events.update_one({ '_id': object_id },
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


# shows a list of all events, and lets you post to add a new event
class EventList(Resource):
    def get(self):
        response = []
        collection = mongo_client.db.events
        events = collection.find()

        for event in events:
            event['_id'] = str(event['_id'])
            response.append(event)

        return { 'response': json.dumps(response, default=str) }

    def post(self):
        args = parser.parse_args()

        mongo_client.db.events.insert_one({
            'host_id': '',
            'name': args['name'],
            'start_date_time': args['start_date_time'],
            'end_date_time': args['end_date_time'],
            'max_guests_allowed': args['max_guests_allowed'],
            'cuisine': args['cuisine'],
            'price_per_person': args['price_per_person'],
            'description': args['description'],
            'guests': args['guests'],
            'published:': True,
            '_view_count:': 0,
            '_created_by_user': '',
            '_created_date_time': datetime.utcnow()
        })

        return '', 201
