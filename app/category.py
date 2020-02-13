from flask import Flask
from flask_restful import reqparse, abort, Resource

app = Flask(__name__)

CATEGORIES = {
    '1': {'name': 'Brazilian'}
}


def abort_if_category_doesnt_exist(category_id):
    if category_id not in CATEGORIES:
        abort(404, message="Category {} doesn't exist".format(category_id))


parser = reqparse.RequestParser()
parser.add_argument('name')


# Category
# shows a single category item and lets you delete a category
class Category(Resource):
    def get(self, category_id):
        abort_if_category_doesnt_exist(category_id)
        return CATEGORIES[category_id]

    def delete(self, category_id):
        abort_if_category_doesnt_exist(category_id)
        del CATEGORIES[category_id]
        return '', 204

    def put(self, category_id):
        args = parser.parse_args()
        name = {'name': args['name']}
        CATEGORIES[category_id] = name
        return name, 201


# CategoryList
# shows a list of all categories, and lets you POST to add new category
class CategoryList(Resource):
    def get(self):
        return CATEGORIES

    def post(self):
        args = parser.parse_args()
        category_id = int(max(CATEGORIES.keys())) + 1
        CATEGORIES[category_id] = {'name': args['name']}
        return CATEGORIES[category_id], 201
