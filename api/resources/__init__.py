from flask_restful import Api

from .auth import Login, Logout
from .event import EventList, Event
from .user import UserList, User


def init_resources(app):
    api = Api(app)

    api.add_resource(EventList, '/resources/v1/events')
    api.add_resource(Event, '/resources/v1/events/<string:id>')
    api.add_resource(UserList, '/resources/v1/users')
    api.add_resource(User, '/resources/v1/users/<string:id>')
    api.add_resource(Login, '/resources/v1/auth/login')
    api.add_resource(Logout, '/resources/v1/auth/logout')