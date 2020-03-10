import unittest
import os

from flask import jsonify
from bson import ObjectId
from datetime import datetime

from api import create_app
from api.resources.constants import HttpStatusCode, Routes
from tests.utils import CustomAssertions, create_event, create_token, create_user

os.environ['FLASK_ENV'] = 'testing'


class TestEventMethods(unittest.TestCase, CustomAssertions):
    def setUp(self):
        self.app = create_app()

        self.user = create_user(self.app)
        self.event = create_event(self.app, str(self.user['_id']))

    def tearDown(self):
        pass

    def test_get_event_invalid_id(self):
        with self.app.test_client() as client:
            # Act
            response = client.get(f'{Routes.EVENTS_V1}/-1')

            # Assert
            self.assert_response(response, b'[HTTP_400_BAD_REQUEST]', HttpStatusCode.HTTP_400_BAD_REQUEST)

    def test_get_event_not_found(self):
        with self.app.test_client() as client:
            # Arrange
            random_id = str(ObjectId())

            # Act
            response = client.get(f'{Routes.EVENTS_V1}/{random_id}')

            # Assert
            self.assert_response(response, b'[HTTP_404_NOT_FOUND]', HttpStatusCode.HTTP_404_NOT_FOUND)

    def test_get_event_successful(self):
        with self.app.test_client() as client:
            # Arrange
            expected_event = self.app.mongo.db.events.find_one({'_id': self.event['_id']})
            expected_event['_id'] = str(expected_event['_id'])

            # Act
            response = client.get(f'{Routes.EVENTS_V1}/{expected_event["_id"]}')

            # Assert
            self.assert_response(response, jsonify({'data': expected_event}).data, HttpStatusCode.HTTP_200_OK)

    def test_put_event_without_token(self):
        with self.app.test_client() as client:
            # Arrange
            event = self.app.mongo.db.events.find_one({'_id': self.event['_id']})

            # Act
            response = client.put(f'{Routes.EVENTS_V1}/{str(event["_id"])}')

            # Assert
            self.assert_response(response, b'[HTTP_403_FORBIDDEN]', HttpStatusCode.HTTP_403_FORBIDDEN)

    def test_put_event_token_expired(self):
        with self.app.test_client() as client:
            # Arrange
            event_id = str(self.event['_id'])

            token = create_token(self.user, -1, self.app.config['SECRET_KEY'])

            self.app.redis.get.return_value = token

            # Act
            response = client.put(f'{Routes.EVENTS_V1}/{event_id}', headers={'Access-Token': token})

            # Assert
            self.assert_response(response, b'[INVALID_TOKEN]', HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_put_event_successful(self):
        with self.app.test_client() as client:
            # Arrange
            event_id = str(self.event['_id'])

            token = create_token(self.user, 60, self.app.config['SECRET_KEY'])

            self.app.redis.get.return_value = token

            fields = {'max_guests_allowed': 8}

            # Act
            response = client.put(f'{Routes.EVENTS_V1}/{event_id}', json=fields, headers={'Access-Token': token})

            # Assert
            self.assert_response(response, b'', HttpStatusCode.HTTP_204_NO_CONTENT)

            event = self.app.mongo.db.events.find_one({'_id': self.event['_id']})
            # TODO: Review this syntax of accessing collection and potentially check phone against event 'collection-view / consolidate-collection'
            self.assertEqual(event['changes'][0]['fields']['max_guests_allowed'], fields['max_guests_allowed'])


class TestEventListMethods(unittest.TestCase, CustomAssertions):
    def setUp(self):
        self.app = create_app()

        self.user = create_user(self.app)
        # self.event = create_event(self.app, str(self.user['_id']))

    def tearDown(self):
        pass

    def test_get_events_sucessful(self):
        with self.app.test_client() as client:
            # Arrange
            collection = self.app.mongo.db.events.find()

            events = []

            for event in collection:
                event['_id'] = str(event['_id'])
                events.append(event)

            # Act
            response = client.get(Routes.EVENTS_V1)

            # Assert
            self.assert_response(response, jsonify({'data': events}).data, HttpStatusCode.HTTP_200_OK)

    def test_post_event_without_request_args(self):
        with self.app.test_client() as client:
            # Arrange
            token = create_token(self.user, 60, self.app.config['SECRET_KEY'])

            # Act
            response = client.post(Routes.EVENTS_V1, headers={'Access-Token' : token})

            # Assert
            self.assertIsNotNone(response.json['message'])

    def test_post_event_successful(self):
        with self.app.test_client() as client:
            # Arrange
            token = create_token(self.user, 60, self.app.config['SECRET_KEY'])

            user_id = str(self.user['_id'])

            event = {
                'host_id': user_id,
                'name': 'foo2',
                'start_datetime': datetime.utcnow().replace(day=5, hour=18),
                'end_datetime': datetime.utcnow().replace(day=5, hour=23),
                'max_guests_allowed': 6,
                'cuisine': ['Brazilian'],
                'price_per_person': 16.0,
                'description': 'Brazilian food by foo2',
                'published:': True,
                'view_count:': 0,
                'created_by_user': user_id,
                'created_datetime': datetime.utcnow()
            }

            # Act
            response = client.post(Routes.EVENTS_V1, json=event, headers={ 'Access-Token': token })

            # Assert
            self.assert_response(response, b'[HTTP_201_CREATED]', HttpStatusCode.HTTP_201_CREATED)


if __name__ == '__main__':
    unittest.main()
