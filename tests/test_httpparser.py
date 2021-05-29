import unittest
from unittest.mock import MagicMock

from httplog.HttpParser import HttpParser


class TestHttpParser(unittest.TestCase):
    def test_correct_parse(self):
        sink = MagicMock()
        stage = HttpParser(sink)

        stage.receive('"10.0.0.2","-","apache",1549573860,"GET /api/user HTTP/1.0",200,1234')
        sink.assert_called()

    def test_incorrect_parse(self):
        sink = MagicMock()
        stage = HttpParser(sink)

        stage.receive('')
        sink.assert_not_called()


if __name__ == '__main__':
    unittest.main()
