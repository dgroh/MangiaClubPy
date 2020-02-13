from flask import Flask
from flask_restful import reqparse, abort, Resource

app = Flask(__name__)

EVENTS = {
    '1': {'name': 'Brazilian 3 Courses'},
    '2': {'name': 'Vegan evening'}
}


def abort_if_event_doesnt_exist(event_id):
    if event_id not in EVENTS:
        abort(404, message="Event {} doesn't exist".format(event_id))


parser = reqparse.RequestParser()
parser.add_argument('name')


# Event
# shows a single event item and lets you delete an event
class Event(Resource):
    def get(self, event_id):
        abort_if_event_doesnt_exist(event_id)
        return EVENTS[event_id]

    def delete(self, event_id):
        abort_if_event_doesnt_exist(event_id)
        del EVENTS[event_id]
        return '', 204

    def put(self, event_id):
        args = parser.parse_args()
        name = {'name': args['name']}
        EVENTS[event_id] = name
        return name, 201


# EventList
# shows a list of all events, and lets you POST to add new events
class EventList(Resource):
    def get(self):
        return EVENTS

    def post(self):
        args = parser.parse_args()
        event_id = int(max(EVENTS.keys())) + 1
        EVENTS[event_id] = {'name': args['name']}
        return EVENTS[event_id], 201