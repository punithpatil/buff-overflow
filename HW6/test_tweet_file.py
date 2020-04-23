import mongomock
import pymongo
import unittest
import unittest.mock
import io

import tweet_file

import templates.model_tweet_response

class TestStdOutListener(unittest.TestCase):
    def test_keywords(self):
        expected_keywords = ['covid19', 'ncov', 'corona', 'coronavirus', 'covid2019']
        self.assertCountEqual(tweet_file.keywords, expected_keywords)

    def test_language(self):
        expected_language = ['en']
        self.assertCountEqual(tweet_file.language, expected_language)

    def test_StdOutListener_on_data(self):
        mock_collection = unittest.mock.MagicMock()
        tweet_file.StdOutListener(mock_collection).on_data(templates.model_tweet_response.tweet_dump)
        assert mock_collection.save.called
        mock_collection.save.assert_called_once_with({'Latitude': 38.65476, 'Longitude': -121.033013, 'hashtags': [], 'username': 'MarieHarlow2'})

    @unittest.mock.patch("tweet_file.print_coordinates")
    def test_StdOutListener_on_data_KeyError(self, mock_print_coordinates):
        tweet_file.StdOutListener(unittest.mock.MagicMock).on_data("{}")
        assert mock_print_coordinates.called
        mock_print_coordinates.assert_called_once_with("\n")

    def test_print_coordinates(self):
        captured_stdout = None
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tweet_file.print_coordinates("Hello, World!")
            captured_stdout = mock_stdout.getvalue()
        self.assertEqual(captured_stdout, "Hello, World!\n")

    def test_StdOutListener_on_error(self):
        captured_stdout = None
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tweet_file.StdOutListener(unittest.mock.MagicMock).on_error("Hello, World!")
            captured_stdout = mock_stdout.getvalue()
        self.assertEqual(captured_stdout, "Hello, World!\n")

    @mongomock.patch(servers=(('server.example.com', 27017),))
    def test_StdOutListener_with_patched_db(self):
        mock_connection = pymongo.MongoClient('server.example.com')
        mock_db = mock_connection.TwitterStream
        mock_db.tweets.ensure_index("id", unique=True, dropDups=True)
        mock_collection = mock_db.tweets
        tweet_file.StdOutListener(mock_collection).on_data(templates.model_tweet_response.tweet_dump)
        response = mock_collection.find_one()
        print("Removed _id: ", response.pop('_id'))
        self.assertDictEqual(response, {'Latitude': 38.65476, 'Longitude': -121.033013, 'hashtags': [], 'username': 'MarieHarlow2'})

class TestIntegrationTestMongoDB(unittest.TestCase):
    def test_actual_mongo_service(self):
        connection = pymongo.MongoClient('localhost', 27017)
        db = connection.TwitterStream
        db.tweets.ensure_index("id", unique=True, dropDups=True)
        collection = db.tweets
        return collection
