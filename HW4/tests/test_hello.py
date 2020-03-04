import unittest

import HW4.app
from HW4 import app

class HelloWorldTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test_hello_app = HW4.app.hello_app.test_client()

    def test_hello_world_response(self):
        response = self.test_hello_app.get('/')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(b'Hello World!', response.data)

    def test_404(self):
        response = self.test_hello_app.get('/other')
        self.assertEqual(response.status, '404 NOT FOUND')

if __name__ == '__main__':
    unittest.main()