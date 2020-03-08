import unittest
from unittest import mock

import os
import jwt

from datetime import datetime
from datetime import timedelta

from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest

from api import create_app
from api.resources.constants import HttpStatusCode, Routes

from tests.utils import CustomAssertions, create_token, create_user
from flask.json import jsonify

os.environ['FLASK_ENV'] = 'testing'


class TestLoginMethods(unittest.TestCase, CustomAssertions):
    def setUp(self):
        self.app = create_app()
        
        create_user(self.app)

    def tearDown(self):
        pass

    def test_post_login_without_email(self):
        with self.app.test_client() as client:
            # Act
            response = client.post(Routes.LOGIN_V1, json={ 'password': 'foo' })
            
            # Assert
            self.assertIsNotNone(response.json['message'].get('email'))
            self.assertIsNone(response.json['message'].get('password'))

    def test_post_login_without_password(self):
        with self.app.test_client() as client:
            # Act
            response = client.post(Routes.LOGIN_V1, json={ 'email': 'foo@foo.com' })
                
            # Assert
            self.assertIsNotNone(response.json['message'].get('password'))
            self.assertIsNone(response.json['message'].get('email'))

    def test_post_login_user_not_found(self):
        with self.app.test_client() as client:
            # Act
            response = client.post(Routes.LOGIN_V1, json={'email': 'not_foo@foo.com', 'password': 'foo'})

            # Assert
            self.assert_response(response, b'[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

    def test_post_login_wrong_password(self):
        with self.app.test_client() as client:
            # Act
            response = client.post(Routes.LOGIN_V1, json={'email': 'foo@foo.com', 'password': 'not_foo'})

            # Assert
            self.assert_response(response, b'[HTTP_401_UNAUTHORIZED]', HttpStatusCode.HTTP_401_UNAUTHORIZED)

    @mock.patch('api.resources.auth.datetime')
    def test_post_login_successful(self, datetime_mock):
        with self.app.test_client() as client:
            # Arrange
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

            # TODO: Consider using create_token from utils. This is an edge case because of the mocked datetime
            expected_token = jwt.encode(expected_payload, self.app.config['SECRET_KEY'], algorithm='HS256').decode(
                'utf-8')

            # Act
            response = client.post(Routes.LOGIN_V1, json={'email': 'foo@foo.com', 'password': 'foo'})

            # Assert
            self.app.redis.setex.assert_called_with(expected_payload['sub'], int(expires_in.total_seconds()),
                                                    expected_token)
            self.assert_response(response, jsonify({'token': expected_token}).data, HttpStatusCode.HTTP_201_CREATED)


class TestLogoutMethods(unittest.TestCase, CustomAssertions):
    def setUp(self):
        self.app = create_app()
        
        create_user(self.app)

    def tearDown(self):
        pass

    def test_delete_logout_without_token(self):
        with self.app.test_client() as client:
            # Act
            response = client.delete(Routes.LOGOUT_V1)

            # Assert
            self.assert_response(response, b'[HTTP_403_FORBIDDEN]', HttpStatusCode.HTTP_403_FORBIDDEN)

    def test_delete_logout_with_token(self):
        with self.app.test_client() as client:
            # Arrange
            user = self.app.mongo.db.users.find_one({'email': 'foo@foo.com'})

            user_id = str(user["_id"])

            token = create_token(user, 60, self.app.config['SECRET_KEY'])
            
            # Act
            response = client.delete(Routes.LOGOUT_V1, headers={ 'Access-Token': token })

            # Assert
            self.app.redis.delete.assert_called_with(f'auth|{user_id}')
            self.assert_response(response, b'', HttpStatusCode.HTTP_204_NO_CONTENT)


if __name__ == '__main__':
    unittest.main()
