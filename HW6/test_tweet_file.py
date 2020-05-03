import mongomock
import pymongo
import unittest
import unittest.mock
import io

import tweet_file

import templates.model_tweet_response

class TestStdOutListener(unittest.TestCase):
    """
    Class to run test suit for "tweet_file". All unit tests are done here
    """
    def test_keywords(self):
        """
        Check constants
        :return: None
        """
        expected_keywords = ['covid19', 'ncov', 'corona', 'coronavirus', 'covid2019']
        self.assertCountEqual(tweet_file.keywords, expected_keywords)

    def test_language(self):
        """
        Check constants
        :return: None
        """
        expected_language = ['en']
        self.assertCountEqual(tweet_file.language, expected_language)

    def test_StdOutListener_on_data(self):
        """
        Check when Twitter stream responds with mocked data.
        Check to see that call to mongo services (mocked) called
        :return: None
        """
        mock_collection = unittest.mock.MagicMock()
        tweet_file.StdOutListener(mock_collection).on_data(templates.model_tweet_response.tweet_dump)
        assert mock_collection.save.called
        mock_collection.save.assert_called_once_with({'Latitude': 38.65476, 'Longitude': -121.033013, 'hashtags': [], 'username': 'MarieHarlow2'})

    @unittest.mock.patch("tweet_file.print_coordinates")
    def test_StdOutListener_on_data_KeyError(self, mock_print_coordinates):
        """
        Check error handling when Twtter stream does not respond with data
        :param mock_print_coordinates: mock out the print_coordinates function
        :return: None
        """
        tweet_file.StdOutListener(unittest.mock.MagicMock).on_data("{}")
        assert mock_print_coordinates.called
        mock_print_coordinates.assert_called_once_with("\n")

    def test_print_coordinates(self):
        """
        Check std print functionality
        :return: None
        """
        captured_stdout = None
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tweet_file.print_coordinates("Hello, World!")
            captured_stdout = mock_stdout.getvalue()
        self.assertEqual(captured_stdout, "Hello, World!\n")

    def test_StdOutListener_on_error(self):
        """
        Check std out outputs expected response
        :return: None
        """
        captured_stdout = None
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tweet_file.StdOutListener(unittest.mock.MagicMock).on_error("Hello, World!")
            captured_stdout = mock_stdout.getvalue()
        self.assertEqual(captured_stdout, "Hello, World!\n")

class TestIntegrationMockedMongoDB(unittest.TestCase):
    """
    Class to perform tests with mocked mongo service using mongomock
    Mongomock can be found here: https://github.com/mongomock/mongomock
    """
    @mongomock.patch(servers=(('server.example.com', 27017),))
    def test_StdOutListener_with_patched_db(self):
        """
        Using mongomock to help test pymongo. Check for working connection
        :return: None
        """
        mock_connection = pymongo.MongoClient('server.example.com')
        mock_db = mock_connection.TwitterStream
        mock_db.tweets.ensure_index("id", unique=True, dropDups=True)
        mock_collection = mock_db.tweets
        tweet_file.StdOutListener(mock_collection).on_data(templates.model_tweet_response.tweet_dump)
        response = mock_collection.find_one()
        print("Removed _id: ", response.pop('_id'))
        self.assertDictEqual(response, {'Latitude': 38.65476, 'Longitude': -121.033013, 'hashtags': [], 'username': 'MarieHarlow2'})

class TestIntegrationMongoDB(unittest.TestCase):
    """
    Class to perform full integration test of the python application and aa mongo database service
    Using TravisCI, we instantiate a mongodb container with default username and passoword.
    Note: To run this test mongo service is required to be installed on localhost:27017 with default username and password
    Default here means, no username and no password
    """
    def test_actual_mongo_service(self):
        """
        Given a mongo services exists
        When the application connects and pushes data into the data base
        Then we should be able to recover the same data from the data base.
        :return: None
        """
        actual_collection = tweet_file.create_mongo_connection()
        tweet_file.StdOutListener(actual_collection).on_data(templates.model_tweet_response.tweet_dump)
        response = actual_collection.find_one()
        print("Removed _id: ", response.pop('_id'))
        self.assertDictEqual(response, {'Latitude': 38.65476, 'Longitude': -121.033013, 'hashtags': [],
                                        'username': 'MarieHarlow2'})
