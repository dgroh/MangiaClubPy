from datetime import datetime
from flask import Flask, jsonify
from flask_restful import Resource, reqparse
from extensions import db


parser = reqparse.RequestParser()
parser.add_argument('name', required=True, help="Name cannot be blank!", location='json')
parser.add_argument('start_date_time', required=True, help="Start date and time musst be a vlida datetime", location='json')
parser.add_argument('end_date_time', required=True, help="End date and time musst be a vlida datetime", location='json')
parser.add_argument('max_guests_allowed', required=True, type=int, location='json')
parser.add_argument('cuisine', action='append', location='json')
parser.add_argument('price_per_person', required=True, type=int, location='json')
parser.add_argument('description', required=True, help="Description cannot be blank!", location='json')
parser.add_argument('guests', action='append', location='json')
parser.add_argument('rating', location='json')


# shows a single event item and lets you delete or update an event
class Event(Resource):
    def get(self, event_id):
        return { 'response': db.events.find_one_or_404({'_id': event_id}) }

    def put(self, event_id):
        event = db.events.find_one_or_404({'_id': event_id})

        args = parser.parse_args()

        parsed_args = dict((key,value) for key,value in args.items() if key is not None)

        fields = []

        event.update({ '_id': event_id },
        {
            '$inc': {
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
        collection = db.events
        events = collection.find()

        for event in events:
             event['_id'] = str(event['_id'])
             response.append(event)

        return { 'response': response }

    def post(self):
        args = parser.parse_args()

        db.events.insert_one({
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
