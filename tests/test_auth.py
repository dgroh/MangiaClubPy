import unittest
from unittest import mock

import os
import bcrypt
import jwt

from datetime import datetime
from datetime import timedelta

from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest

from api import create_app
from api.resources.auth import Login, Logout
from api.resources.constants import HttpStatusCode

os.environ['FLASK_ENV'] = 'testing'


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


class TestLoginMethods(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        
        create_user(self.app)

        self.login = Login()

    def tearDown(self):
        pass

    def test_post_auth_login_without_request_args(self):
        with self.app.test_request_context():
            self.assertRaises(BadRequest, self.login.post)

    def test_post_auth_login_without_email(self):
        with self.app.test_client() as request_ctx:
            # Arrange
            request_ctx.request.values = MultiDict([('password', 'foo')])

            # Act and Assert
            with self.assertRaises(BadRequest) as error_ctx:
                self.login.post()
                
            self.assertEqual(error_ctx.exception.data['message']['email'], 'Missing required parameter in the JSON body or the post '
                                                             'body or the query string')

    def test_post_auth_login_without_password(self):
        with self.app.test_request_context() as request_ctx:
            # Arrange
            request_ctx.request.values = MultiDict([('email', 'foo@foo.com')])

            # Act and Assert
            with self.assertRaises(BadRequest) as error_ctx:
                self.login.post()
            
            self.assertEqual(error_ctx.exception.data['message']['password'], 'Missing required parameter in the JSON body or the post '
                                                             'body or the query string')

    @mock.patch('api.resources.auth.make_response')
    def test_post_auth_login_user_not_found(self, make_response_mock):
        with self.app.app_context() as app_ctx, self.app.test_request_context() as request_ctx:
            # Arrange
            request_ctx.request.values = MultiDict([('email', 'not_foo@foo.com'), ('password', 'foo')])

            # Act
            self.login.post()

            # Assert
            make_response_mock.assert_called_with('[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

    @mock.patch('api.resources.auth.make_response')
    def test_post_auth_login_wrong_password(self, make_response_mock):
        with self.app.app_context() as app_ctx, self.app.test_request_context() as request_ctx:
            # Arrange
            request_ctx.request.values = MultiDict([('email', 'foo@foo.com'), ('password', 'not_foo')])

            # Act
            self.login.post()

            # Assert
            make_response_mock.assert_called_with('[HTTP_401_UNAUTHORIZED]', HttpStatusCode.HTTP_401_UNAUTHORIZED)

    @mock.patch('api.resources.auth.make_response')
    @mock.patch('api.resources.auth.datetime')
    def test_post_auth_login_successful(self, datetime_mock, make_response_mock):
        with self.app.app_context() as app_ctx, self.app.test_request_context() as request_ctx:
            # Arrange
            request_ctx.request.values = MultiDict([('email', 'foo@foo.com'), ('password', 'foo')])

            user = self.app.mongo.db.users.find_one({'email': 'foo@foo.com'})

            datetime_mock.utcnow = mock.Mock(return_value=datetime(1901, 12, 21))

            expires_in = timedelta(days=60)

            expected_payload = {
                'exp': datetime_mock.utcnow.return_value + expires_in,
                'iat': datetime_mock.utcnow.return_value,
                'sub': f'auth|{str(user["_id"])}',
                'email': user['email'],
                'phone:': user['phone']
            }

            expected_token = jwt.encode(expected_payload, self.app.config['SECRET_KEY'], algorithm='HS256').decode(
                'utf-8')

            self.app.redis = mock.Mock()

            # Act
            self.login.post()

            # Assert
            self.app.redis.setex.assert_called_with(expected_payload['sub'], int(expires_in.total_seconds()),
                                                    expected_token)
            make_response_mock.assert_called_with({'token': expected_token}, HttpStatusCode.HTTP_201_CREATED)


class TestLogoutMethods(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        
        create_user(self.app)

        self.logout = Logout()

    def tearDown(self):
        pass

    @mock.patch('api.resources.auth.make_response')
    def test_delete_auth_token_not_in_header(self, make_response_mock):
        with self.app.test_request_context():
            # Act
            self.logout.delete()

            # Assert
            make_response_mock.assert_called_with('[HTTP_403_FORBIDDEN]', HttpStatusCode.HTTP_403_FORBIDDEN)

    def test_delete_auth_with_token(self):
        with self.app.app_context():
            # Arrange
            user = self.app.mongo.db.users.find_one({'email': 'foo@foo.com'})

            user_id = str(user["_id"])

            expires_in = timedelta(days=60)

            payload = {
                'exp': datetime.utcnow() + expires_in,
                'iat': datetime.utcnow(),
                'sub': f'auth|{user_id}',
                'email': user['email'],
                'phone:': user['phone']
            }

            token = jwt.encode(payload, self.app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

            # Act
            with self.app.test_request_context(environ_base={'HTTP_ACCESS_TOKEN': token}):
                result = self.logout.delete()

            # Assert
            self.app.redis.delete.assert_called_with(f'auth|{user_id}')
            self.assertEqual(result, ('[HTTP_204_NO_CONTENT]', 204))


if __name__ == '__main__':
    unittest.main()
