import unittest
from unittest import mock
from unittest.mock import MagicMock

from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest

from api.resources.auth import Login


@mock.patch('flask_restful.reqparse.request')
@mock.patch('flask_restful.reqparse.current_app', MagicMock())
class TestLoginMethods(unittest.TestCase):
    def setUp(self):
        self.login = Login()
        pass

    def tearDown(self):
        pass

    def test_post_request_without_args(self, request_mock):
        try:
            self.login.post()
        except Exception as e:
            self.assertTrue(isinstance(e, BadRequest))

    def test_post_request_without_email(self, request_mock):
        try:
            request_mock.values.return_value = MultiDict([('password', 'foo')])
            self.login.post()
        except Exception as e:
            self.assertTrue(isinstance(e, BadRequest))
            self.assertEqual(e.data['message']['email'], 'Missing required parameter in the JSON body or the post '
                                                         'body or the query string')

    def test_post_request_without_password(self, request_mock):
        try:
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com')])
            self.login.post()
        except Exception as e:
            self.assertTrue(isinstance(e, BadRequest))
            self.assertEqual(e.data['message']['password'], 'Missing required parameter in the JSON body or the post '
                                                            'body or the query string')

    def test_post_request_user_not_found(self, request_mock):
        with mock.patch('api.resources.auth.app') as app:
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com'), ('password', 'foo')])
            # TODO: WIP

    def test_post_request_wrong_password(self, request_mock):
        with mock.patch('api.resources.auth.app'):
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com'), ('password', 'foo')])
            # TODO: WIP

    def test_post_request_successful(self, request_mock):
        with mock.patch('api.resources.auth.app'):
            request_mock.values.return_value = MultiDict([('email', 'foo@foo.com'), ('password', 'foo')])
            # TODO: WIP


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
