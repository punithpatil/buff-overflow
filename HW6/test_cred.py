import unittest
import unittest.mock

import cred

class TestCredentials(unittest.TestCase):
    """
    This class will test the existance of constants for Twitter Auth
    """
    def test_consumer_key(self):
        with unittest.mock.patch("cred.consumer_key", "mock_consumer_key"):
            self.assertEqual(cred.consumer_key, "mock_consumer_key")

    def test_consumer_secret(self):
        with unittest.mock.patch("cred.consumer_secret", "mock_consumer_secret"):
            self.assertEqual(cred.consumer_secret, "mock_consumer_secret")

    def test_access_token(self):
        with unittest.mock.patch("cred.access_token", "mock_access_token"):
            self.assertEqual(cred.access_token, "mock_access_token")

    def test_access_secret(self):
        with unittest.mock.patch("cred.access_secret", "mock_access_secret"):
            self.assertEqual(cred.access_secret, "mock_access_secret")

