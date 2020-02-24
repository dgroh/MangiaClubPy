from datetime import datetime
from flask import Flask, jsonify
from flask_restful import Resource, reqparse
from db import mongo
from bson import ObjectId

parser = reqparse.RequestParser()
parser.add_argument('name', location='json')
parser.add_argument('start_date_time', location='json')
parser.add_argument('end_date_time', location='json')
parser.add_argument('max_guests_allowed', type=int, location='json')
parser.add_argument('cuisine', action='append', location='json')
parser.add_argument('price_per_person', type=float, location='json')
parser.add_argument('description', location='json')
parser.add_argument('guests', action='append', location='json')
parser.add_argument('rating', location='json')

class Event(Resource):
    def get(self, event_id):
        object_id = ObjectId(event_id)

        event = mongo.db.events.find_one_or_404({'_id': object_id})

        event['_id'] = str(event['_id'])

        return jsonify({'data': event})

    def put(self, event_id):
        object_id = ObjectId(event_id)

        events = mongo.db.events

        events.find_one_or_404({'_id': object_id})

        args = parser.parse_args()

        fields = {key: value for key,
                  value in args.items() if value is not None}

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

        return '', 204


class EventList(Resource):
    def get(self):
        response = []
        events = mongo.db.events.find()

        for event in events:
            event['_id'] = str(event['_id'])
            response.append(event)

        return jsonify({'data': response})

    def post(self):
        args = parser.parse_args()

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
            'guests': args['guests'],
            'published:': True,
            '_view_count:': 0,
            '_created_by_user': '',
            '_created_date_time': datetime.utcnow()
        })

        return '', 201
