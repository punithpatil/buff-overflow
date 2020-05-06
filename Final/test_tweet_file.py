import mongomock
import pymongo
import unittest
import unittest.mock
import pandas
import pandas.testing
import io
import json

import tweet_file

import test_stubs.model_tweet_response
import test_stubs.model_std_output
import test_stubs.model_mongo_response
import test_stubs.model_hashtagsplot_std_response
import test_stubs.model_print_top5_liked_tweets_response

class TestTextTokenizerFormatter(unittest.TestCase):
    def test_prepared_tweet(self):
        actual_response = tweet_file.prepare_Tweet(json.loads(test_stubs.model_tweet_response.tweet_dump))
        self.assertDictEqual(actual_response,test_stubs.model_tweet_response.prepared_tweet_response)

    def test_tweet_tokenizer(self):
        test_sentence = "Hello, World! Check if alphanumeric words 12j09 are removed"
        expected_reponse = ['hello', 'world', 'check', 'alphanumeric', 'words', '12j09', 'are', 'removed']
        self.assertListEqual(tweet_file.tweet_tokenizer(test_sentence), expected_reponse)

class TestDataFormaters(unittest.TestCase):
    def setUp(self) -> None:
        self.mongo_pandas_frame = pandas.DataFrame(test_stubs.model_mongo_response.model_mongo_response)
    def test_prepare_df(self):
        actual_data_frame_old, actual_data_frame_new = tweet_file.prepare_df(test_stubs.model_mongo_response.model_mongo_response)
        pandas.testing.assert_frame_equal(self.mongo_pandas_frame, actual_data_frame_old)

    def test_print_top5_liked_tweets(self):
        captured_stdout = None
        expected_output = test_stubs.model_print_top5_liked_tweets_response.model_print_top5_liked_tweets_response
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tweet_file.print_top5_liked_tweets(self.mongo_pandas_frame)
            captured_stdout = mock_stdout.getvalue()
        self.assertEqual(captured_stdout, expected_output)

    def test_saveplot(self):
        tweet_file.saveplot(self.mongo_pandas_frame)

    def test_hashtagsplot(self):
        captured_stdout = None
        expected_output = test_stubs.model_hashtagsplot_std_response.model_hashtagsplot_std_response
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tweet_file.hashtagsplot(self.mongo_pandas_frame)
            captured_stdout = mock_stdout.getvalue()
        self.assertEqual(captured_stdout, expected_output)

    def test_get_frequent_terms(self):
        expected_output = pandas.read_csv("test_stubs/model_frequent_terms_reponse_dump.csv", index_col = 0)
        actual_output = tweet_file.get_frequent_terms(self.mongo_pandas_frame["Tweet_text"], stop_words="english")
        pandas.testing.assert_frame_equal(actual_output, expected_output)

