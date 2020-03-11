import unittest
import jwt
import bcrypt

from datetime import datetime, timedelta


def create_event(app, user_id):
    """
    This function creates a test event in mongomock to be used throughout the tests
    """

    event = {
        'host_id': user_id,
        'name': 'foo',
        'start_datetime': datetime.utcnow().replace(hour=18),
        'end_datetime': datetime.utcnow().replace(hour=23),
        'max_guests_allowed': 6,
        'cuisine': ['Japanese'],
        'price_per_person': 16.0,
        'description': 'Japanese food by foo',
        'published:': True,
        'view_count:': 0,
        'created_by_user': user_id,
        'created_datetime': datetime.utcnow()
    }

    inserted_id = app.mongo.db.events.insert_one(event).inserted_id

    return app.mongo.db.events.find_one({ '_id': inserted_id })

def create_user(app):
    """
    This function creates a test user in mongomock to be used throughout the tests
    """
    password_salt = bcrypt.gensalt()

    user = {
        'email': 'foo@foo.com',
        'first_name': 'foo',
        'last_name': 'foo',
        'hashed_password': bcrypt.hashpw('foo'.encode('utf-8'), password_salt),
        'password_salt': password_salt,
        'phone': '+4915162961189',
        'published:': True,
        'created_datetime': datetime.utcnow()
    }

    app.mongo.db.users.insert_one(user)

    return app.mongo.db.users.find_one({ 'email': user['email'] })


def create_token(user, expiration: int, secret: str):
    """
    This function creates a jwt token for the test user

    :param user: The user to be encoded (`_id`, `email` and `phone` are required attributes). 
    :param expiration: The expiration in days
    :param secret: The token secret
    :return: A jwt token

    """

    user_id = str(user['_id'])

    payload = {
        'exp': datetime.utcnow() + timedelta(days=expiration),
        'iat': datetime.utcnow(),
        'sub': f'auth|{user_id}',
        'email': user['email'],
        'phone:': user['phone']
    }

    return jwt.encode(payload, secret, algorithm='HS256').decode('utf-8')


class CustomAssertions:
    def __init__(self):
        unittest.TestCase.maxDiff = None

    """
    A class to store custom assertions.
    """

    def assert_response(self, response, data: bytes, status_code: int):
        """
        Asserts a response message based on the message and status code returned from the test_client.

        :param response: The response result of the client call
        :param data: The message data expected from the response
        :param status_code: The http status code expected from the response

        ```
        def test_name(self):
            with self.app.test_client() as client:
                # Act
                response = client.delete('/route/to/the/endpoint')

                # Assert
                self.assert_response(response, 'Access Forbidden', 403)
        ```
        """
        
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status_code)
