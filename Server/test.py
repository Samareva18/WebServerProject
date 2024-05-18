import unittest
from unittest.mock import MagicMock, Mock
from Server.handle_request import HandleRequest
import errors
from parse_request import ParseRequest


class TestHandleRequest(unittest.TestCase):

    def setUp(self):
        self.request = MagicMock()
        self.handle_request = HandleRequest(self.request)

    def test_check_method_implement(self):
        self.request.method = 'GET'
        self.handle_request.check_method_implement()

        self.request.method = 'POST'
        with self.assertRaises(errors.NotImplementedMethodError):
            self.handle_request.check_method_implement()

    def test_check_bad_request(self):
        self.request.method = 'GET'
        self.request.target = '/index.html'
        self.request.version = 'HTTP/1.1'
        self.request.headers = {'Host': 'example.com'}
        self.handle_request.check_bad_request()

        self.request.target = None
        with self.assertRaises(errors.BadRequestError):
            self.handle_request.check_bad_request()

        self.request.headers = {}
        with self.assertRaises(errors.BadRequestError):
            self.handle_request.check_bad_request()


class TestParseRequest(unittest.TestCase):

    def setUp(self):
        self.request_data = "GET /index.html HTTP/1.1\r\nHost: example.com\r\nContent-Type: text/html\r\n\r\nThis is the body"
        self.log = Mock()
        self.parser = ParseRequest(self.request_data, self.log)

    def test_parse_request_line(self):
        self.parser.request = self.request_data
        parsed_line = self.parser.parse_request_line()

        self.assertEqual(parsed_line, ["GET", "/index.html", "HTTP/1.1"])

    def test_parse_request_body(self):
        self.parser.request = self.request_data
        parsed_body = self.parser.parse_request_body()

        self.assertEqual(parsed_body, "This is the body")

    def test_parse_request_headers(self):
        self.parser.request = self.request_data
        parsed_headers = self.parser.parse_request_headers()

        self.assertEqual(parsed_headers["Host"], "example.com")
        self.assertEqual(parsed_headers["Content-Type"], "text/html")


if __name__ == '__main__':
    unittest.main()
