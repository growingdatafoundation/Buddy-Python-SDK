import mock
import time
import unittest

import buddy
from settings import Settings
from test_base import TestBase


class Test7(TestBase):

    @mock.patch('buddy_client.Settings')
    def test_create_user(self, settings_mock):
        settings_mock.return_value = Settings(TestBase.US_app_id)

        self.setup_with_bad_tokens(settings_mock.return_value)

        buddy.init(TestBase.US_app_id, TestBase.US_app_key, "test_create_user")

        users = buddy.get("/users")
        self.assertIsNotNone(users)

        device_token = settings_mock.return_value.access_token_string
        self.assertIsNotNone(device_token)

        user_response = self.create_test_user()
        self.assertIsNotNone(user_response)

        user_token = settings_mock.return_value.access_token_string
        self.assertIsNotNone(user_token)

        self.assertNotEqual(device_token, user_token)

        self.assertEqual(buddy.current_user_id, user_response["result"]["id"])

    @mock.patch('buddy_client.Settings')
    def test_create_logout_login_user(self, settings_mock):
        settings_mock.return_value = Settings(TestBase.US_app_id)

        self.setup_with_bad_tokens(settings_mock.return_value)

        buddy.init(TestBase.US_app_id, TestBase.US_app_key, "test_create_logout_login_user")

        users_response = buddy.get("/users")
        self.assertIsNotNone(users_response)

        device_token = settings_mock.return_value.access_token_string

        user_name = self.get_test_user_name()
        user1_response = self.create_test_user(user_name)
        self.assertIsNotNone(user1_response)

        user_token = settings_mock.return_value.access_token_string

        buddy.logout_user()

        device_token_2 = settings_mock.return_value.access_token_string

        self.assertEqual(device_token, device_token_2)
        self.assertNotEqual(device_token, user_token)
        self.assertNotEqual(device_token_2, user_token)

        user2_response = buddy.login_user(user_name, self.get_test_user_password())
        self.assertIsNotNone(user2_response)

        self.assertEqual(user1_response["result"]["id"], user2_response["result"]["id"])
        self.assertEqual(buddy.current_user_id, user2_response["result"]["id"])

    def test_upload_pic(self):
        buddy.init(TestBase.US_app_id, TestBase.US_app_key, "test_upload_pic")

        self.create_test_user()

        # TODO: to run in Python Tools for VS, change to "tests\Buddy Logo.png"
        response = buddy.post("/pictures", {}, file=(open("Buddy Logo.png", "rb"), "image/png"))
        self.assertIsNotNone(response)
        self.assertIsNotNone(response["result"]["signedUrl"])

    @mock.patch('buddy_client.Settings')
    def test_auth_error(self, settings_mock):
        settings_mock.return_value = Settings(TestBase.US_app_id)
        self.setup_with_bad_tokens(settings_mock.return_value)

        buddy.init(TestBase.US_app_id, TestBase.US_app_key, "test_auth_error")

        response = buddy.get("/pictures")
        self.assertIsNotNone(response)
        self.assertEqual(response["status"], 403)

    def test_auth(self):
        buddy.init(TestBase.US_app_id, TestBase.US_app_key, "test_auth")

        logger = AuthLogger()

        self.create_test_user()

        buddy.logout_user()

        buddy.authentication_needed.on_change += logger.log

        response = buddy.get("/pictures", {})
        self.assertIsNotNone(response)

        while logger.authorized is not True:
            time.sleep(2)

    def test_last_location(self):
        buddy.init(TestBase.US_app_id, TestBase.US_app_key, "test_last_location")

        self.create_test_user()

        location = (42.0, -42.0)
        buddy.last_location = location

        response = buddy.post("/checkins", {})
        self.assertIsNotNone(response)
        result = response["result"]
        self.assertIsNotNone(result)

        response = buddy.get("/checkins/" + result["id"])
        self.assertIsNotNone(response)
        result = response["result"]
        self.assertIsNotNone(result)
        self.assertEqual(result["location"], {u'lat': location[0], u'lng': location[1]})


class AuthLogger(object):
    def __init__(self):
        self.authorized = False

    def log(self):
        self.authorized = True

if __name__ == '__main__':
    unittest.main()
