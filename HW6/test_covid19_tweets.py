import unittest
import unittest.mock

import covid19_tweets

class TestStdOutListener(unittest.TestCase):
    def test_keywords(self):
        expected_keywords = ['covid19', 'ncov', 'corona', 'coronavirus', 'covid2019']
        self.assertCountEqual(covid19_tweets.keywords, expected_keywords)

    def test_language(self):
        expected_language = ['en']
        self.assertCountEqual(covid19_tweets.language, expected_language)

    @unittest.mock.patch("json.loads")
    def test_StdOutListener(self, mock_json_load):
        # TODO: get dummy model response set up
        mock_json_load.return_value = {}
        covid19_tweets.StdOutListener().on_data("{}")
