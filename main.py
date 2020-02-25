from flask import Flask
from flask_restful import Api

from resources.event import Event, EventList
from resources.user import User, UserList
from resources.auth import Login

app = Flask(__name__)
api = Api(app)

##
# Actually setup the Api resource routing here
##
api.add_resource(EventList, '/api/v1/events')
api.add_resource(Event, '/api/v1/events/<string:id>')
api.add_resource(UserList, '/api/v1/users')
api.add_resource(User, '/api/v1/users/<string:id>')
api.add_resource(Login, '/api/v1/auth/login')

if __name__ == '__main__':
    app.run()