from flask_restful import Api

from main import app
from api.resources.auth import Login, Logout
from api.resources.event import EventList, Event
from api.resources.user import UserList, User

api = Api(app)

##
# Actually setup the Api resource routing here
##
api.add_resource(EventList, '/api/v1/events')
api.add_resource(Event, '/api/v1/events/<string:id>')
api.add_resource(UserList, '/api/v1/users')
api.add_resource(User, '/api/v1/users/<string:id>')
api.add_resource(Login, '/api/v1/auth/login')
api.add_resource(Logout, '/api/v1/auth/logout')
