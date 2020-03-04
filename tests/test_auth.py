import unittest
from unittest import mock
from unittest.mock import MagicMock

import bcrypt

from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest

from api.auth import Login
from api.constants import HttpStatusCode


@mock.patch('api.auth.reqparse.request')
@mock.patch('api.auth.reqparse.current_app', MagicMock())
class TestLoginMethods(unittest.TestCase):
    def setUp(self):
        self.login = Login()
        pass

    def tearDown(self):
        pass

    def test_post_request_without_args(self, request_mock):
        self.assertRaises(BadRequest, self.login.post)

    def test_post_request_without_email(self, request_mock):
        # Arrange
        request_mock.values.return_value = MultiDict([('password', 'foo')])

        # Act and Assert
        with self.assertRaises(BadRequest) as e:
            self.login.post()
            self.assertEqual(e.data['message']['email'], 'Missing required parameter in the JSON body or the post '
                                                         'body or the query string')

    def test_post_request_without_password(self, request_mock):
        # Arrange
        request_mock.values.return_value = MultiDict([('email', 'foo@foo.com')])

        # Act and Assert
        with self.assertRaises(BadRequest) as e:
            self.login.post()
            self.assertEqual(e.data['message']['password'], 'Missing required parameter in the JSON body or the post '
                                                            'body or the query string')

    @mock.patch('api.auth.make_response')
    def test_post_request_user_not_found(self, make_response_mock, request_mock):
        with mock.patch('api.auth.app') as app:
            # Arrange
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com'), ('password', 'foo')])
            app.mongo.db.users.find_one.return_value = None
            
            # Act
            self.login.post()
            
            # Assert
            make_response_mock.assert_called_with('[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

    @mock.patch('api.auth.make_response')
    def test_post_request_wrong_password(self, make_response_mock, request_mock):
        with mock.patch('api.auth.app') as app:
            # Arrange
            hashed_password = bcrypt.hashpw('foo'.encode('utf-8'), bcrypt.gensalt())
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com'), ('password', 'not_foo')])
            found_user = { "hashed_password": hashed_password }
            app.mongo.db.users.find_one.return_value = found_user

            # Act
            self.login.post()
            
            # Assert
            make_response_mock.assert_called_with('[HTTP_401_UNAUTHORIZED]', HttpStatusCode.HTTP_401_UNAUTHORIZED)


    @mock.patch('api.auth.make_response')
    @mock.patch('api.auth.jwt')
    def test_post_request_successful(self, jwt_mock, make_response_mock, request_mock):
        with mock.patch('api.auth.app') as app:
            # Arrange
            hashed_password = bcrypt.hashpw('foo'.encode('utf-8'), bcrypt.gensalt())
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com'), ('password', 'foo')])
            found_user = {'_id': 'abcd1234', 'phone': '01234567789', 'hashed_password': hashed_password }
            app.mongo.db.users.find_one.return_value = found_user
            jwt_mock.encode.return_value = b'the_foo_token'
            
            # Act
            self.login.post()
            
            # Assert
            # TODO: Assert if a real toke is returnin and if it has been passed to redis with token sub
            jwt_mock.encode.assert_called()
            app.redis.setex.assert_called()
            make_response_mock.assert_called_with({'token': 'the_foo_token'}, HttpStatusCode.HTTP_201_CREATED)


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
