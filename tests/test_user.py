import unittest
from unittest import mock

from datetime import datetime
from bson.objectid import ObjectId
import bcrypt

from api import create_app
from api.resources.user import User
from api.resources.constants import HttpStatusCode


def create_user(app):
    """
    Create a test user in mongomock to be used throughout the tests
    """
    password_salt = bcrypt.gensalt()

    user = {
        'email': 'foo@foo.com',
        'first_name': 'foo',
        'last_name': 'foo',
        'hashed_password': bcrypt.hashpw('foo'.encode('utf-8'), password_salt),
        'password_salt': password_salt,
        'phone': '15162961189',
        'published:': True,
        'created_datetime': datetime.utcnow()
    }

    app.mongo.db.users.insert_one(user)


@mock.patch('api.resources.user.reqparse.request')
class TestUserMethods(unittest.TestCase):
    def setUp(self):
        self.app = create_app()

        create_user(self.app)

        self.user = User()

    def tearDown(self):
        pass

    @mock.patch('api.resources.user.make_response')
    def test_get_user_invalid_id(self, make_response_mock, request_mock):
        with self.app.app_context():
            # Act
            self.user.get(-1)
            
            # Assert
            make_response_mock.assert_called_with('[HTTP_400_BAD_REQUEST]', HttpStatusCode.HTTP_400_BAD_REQUEST)

    @mock.patch('api.resources.user.make_response')
    def test_get_user_not_found(self, make_response_mock, request_mock):
        with self.app.app_context():
            # Arrange
            random_id = str(ObjectId())

            # Act
            self.user.get(random_id)
            
            # Assert
            make_response_mock.assert_called_with('[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

    @mock.patch('api.resources.user.make_response')
    def test_get_user_successful(self, make_response_mock, request_mock):
        with self.app.app_context():
            # Arrange
            expected_user = self.app.mongo.db.users.find_one({ 'email': 'foo@foo.com' })
            expected_user['_id'] = str(expected_user['_id'])
            expected_user['hashed_password'] = expected_user['hashed_password'].decode('utf-8')
            expected_user['password_salt'] = expected_user['password_salt'].decode('utf-8')

            # Act
            self.user.get(expected_user['_id'])

            # Assert
            make_response_mock.assert_called_with({'data': expected_user}, HttpStatusCode.HTTP_200_OK)

    @mock.patch('api.resources.user.make_response')
    def test_put_user_without_token(self, make_response_mock, request_mock):
        with self.app.app_context():
            pass

    @mock.patch('api.resources.user.make_response')
    def test_put_user_not_found(self, make_response_mock, request_mock):
        with self.app.app_context():
            pass

    @mock.patch('api.resources.user.make_response')
    def test_put_user_successful(self, make_response_mock, request_mock):
        with self.app.app_context():
            pass


# WIP
class TestUserListMethods(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_post_user_without_token(self):
        pass

    def test_post_user_already_exists(self):
        pass

    def test_post_user_successful(self):
        pass


if __name__ == '__main__':
    unittest.main()
