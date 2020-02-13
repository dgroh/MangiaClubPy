from flask import Flask
from flask_restful import Api
from category import Category, CategoryList
from event import Event, EventList

app = Flask(__name__)
api = Api(app)

##
# Actually setup the Api resource routing here
##
api.add_resource(EventList, '/api/v1/events')
api.add_resource(Event, '/api/v1/events/<string:event_id>')
api.add_resource(CategoryList, '/api/v1/categories')
api.add_resource(Category, '/api/v1/categories/<string:category_id>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')