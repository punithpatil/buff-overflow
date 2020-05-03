import unittest
import unittest.mock
import io

import covid19_tweets

import templates.model_tweet_response


class TestStdOutListener(unittest.TestCase):
    """
    Class to run unit test for covid19_tweets file
    """
    def test_keywords(self):
        """
        Test constants
        :return: None
        """
        expected_keywords = ['covid19', 'ncov', 'corona', 'coronavirus', 'covid2019']
        self.assertCountEqual(covid19_tweets.keywords, expected_keywords)

    def test_language(self):
        """
        Test constants
        :return: None
        """
        expected_language = ['en']
        self.assertCountEqual(covid19_tweets.language, expected_language)

    @unittest.mock.patch("covid19_tweets.print_coordinates")
    def test_StdOutListener_on_data(self, mock_print_coordinates):
        """
        Check when Twitter stream responds with mocked data.
        Check to see that call to mocked print_coordinates is called
        :param mock_print_coordinates:
        :return: None
        """
        covid19_tweets.StdOutListener().on_data(templates.model_tweet_response.tweet_dump)
        assert mock_print_coordinates.called
        mock_print_coordinates.assert_called_once_with([[[-121.033013, 38.65476], [-121.033013, 38.726092], [-120.924554, 38.726092], [-120.924554, 38.65476]]])

    @unittest.mock.patch("covid19_tweets.print_coordinates")
    def test_StdOutListener_on_data_KeyError(self, mock_print_coordinates):
        """
         Check error handling when Twtter stream does not respond with data
        :param mock_print_coordinates: mock out the print_coordinates function
        :return: None
        """
        covid19_tweets.StdOutListener().on_data("{}")
        assert mock_print_coordinates.called
        mock_print_coordinates.assert_called_once_with("\n")

    def test_print_coordinates(self):
        """
        Check std print functionality
        :return: None
        """
        captured_stdout = None
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            covid19_tweets.print_coordinates("Hello, World!")
            captured_stdout = mock_stdout.getvalue()
        self.assertEqual(captured_stdout, "Hello, World!\n")

    def test_StdOutListener_on_error(self):
        """
        Check std out outputs expected response
        :return: None
        """
        captured_stdout = None
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            covid19_tweets.StdOutListener().on_error("Hello, World!")
            captured_stdout = mock_stdout.getvalue()
        self.assertEqual(captured_stdout, "Hello, World!\n")



