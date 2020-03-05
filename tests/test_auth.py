import unittest
from unittest import mock
from unittest.mock import MagicMock

import os
import bcrypt
import mongomock
import jwt

from datetime import datetime
from datetime import timedelta

from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest

from api import create_app
from api.resources.auth import Login
from api.resources.constants import HttpStatusCode

os.environ['FLASK_ENV'] = 'testing'


@mock.patch('api.resources.auth.reqparse.request')
class TestLoginMethods(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.mongo.db.users.insert_one(self.user)
        self.login = Login()
        pass

    def tearDown(self):
        pass

    def test_post_request_without_args(self, request_mock):
        with self.app.app_context():
            self.assertRaises(BadRequest, self.login.post)

    def test_post_request_without_email(self, request_mock):
        with self.app.app_context():
            # Arrange
            request_mock.values.return_value = MultiDict([('password', 'foo')])

            # Act and Assert
            with self.assertRaises(BadRequest) as e:
                self.login.post()
                self.assertEqual(e.data['message']['email'], 'Missing required parameter in the JSON body or the post '
                                                             'body or the query string')

    def test_post_request_without_password(self, request_mock):
        with self.app.app_context():
            # Arrange
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com')])

            # Act and Assert
            with self.assertRaises(BadRequest) as e:
                self.login.post()
                self.assertEqual(e.data['message']['password'],
                                 'Missing required parameter in the JSON body or the post '
                                 'body or the query string')

    @mock.patch('api.resources.auth.make_response')
    def test_post_request_user_not_found(self, make_response_mock, request_mock):
        with self.app.app_context():
            # Arrange
            request_mock.values.return_value = MultiDict([('email', 'not_foo@foo.com'), ('password', 'foo')])

            # Act
            self.login.post()

            # Assert
            make_response_mock.assert_called_with('[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

    @mock.patch('api.resources.auth.make_response')
    def test_post_request_wrong_password(self, make_response_mock, request_mock):
        with self.app.app_context():
            # Arrange
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com'), ('password', 'not_foo')])

            # Act
            self.login.post()

            # Assert
            make_response_mock.assert_called_with('[HTTP_401_UNAUTHORIZED]', HttpStatusCode.HTTP_401_UNAUTHORIZED)

    @mock.patch('api.resources.auth.make_response')
    @mock.patch('api.resources.auth.datetime')
    def test_post_request_successful(self, mock_datetime, make_response_mock, request_mock):
        with self.app.app_context():
            # Arrange
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com'), ('password', 'foo')])

            user = self.app.mongo.db.users.find_one({'email': 'foo@foo.com'})

            mock_datetime.utcnow = mock.Mock(return_value=datetime(1901, 12, 21))

            expires_in = timedelta(days=60)

            expected_payload = {
                'exp': mock_datetime.utcnow.return_value + expires_in,
                'iat': mock_datetime.utcnow.return_value,
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

    @property
    def user(self):
        password_salt = bcrypt.gensalt()

        return {
            'email': 'foo@foo.com',
            'first_name': 'foo',
            'last_name': 'foo',
            'hashed_password': bcrypt.hashpw('foo'.encode('utf-8'), password_salt),
            'password_salt': password_salt,
            'phone': '15162961189',
            'published:': True,
            'created_datetime': datetime.utcnow()
        }


class TestLogoutMethods(unittest.TestCase):
    def setUp(self):
        # TODO: WIP
        pass

    def tearDown(self):
        # TODO: WIP
        pass

    def test_delete_without_token(self):
        # TODO: WIP
        pass

    def test_delete_with_token(self):
        # TODO: WIP
        pass


if __name__ == '__main__':
    unittest.main()
