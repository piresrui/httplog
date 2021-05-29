import unittest
from copy import deepcopy
from datetime import datetime
from unittest.mock import Mock

from httplog.Metrics import Metrics, Data, Snapshot


class DataTest(unittest.TestCase):
    def test_copy(self):
        expected = Data(
            host="",
            user="",
            date=datetime.now(),
            path="",
            verb="",
            rfc981="",
            length="",
            status=200
        )

        actual = deepcopy(expected)
        self.assertEqual(actual.date, expected.date)


class MetricsTest(unittest.TestCase):
    def test_data_updated_without_error(self):
        sink = SinkMock(actual=Snapshot())
        metrics = Metrics(sink)

        curr_time = datetime.now()
        metrics.receive(Data(
            date=curr_time,
            host="test",
            rfc981="",
            user="",
            verb="GET",
            path="/test",
            length="100",
            status=200
        ))

        self.assertEqual(sink.actual.latest_access, curr_time)
        self.assertEqual(sink.actual._requests, 1)
        self.assertEqual(sink.actual._average_size, 100)
        self.assertEqual(sink.actual._errors, 0)

    def test_data_updated_with_error(self):
        sink = SinkMock(actual=Snapshot())
        metrics = Metrics(sink)

        curr_time = datetime.now()
        metrics.receive(Data(
            date=curr_time,
            host="test",
            rfc981="",
            user="",
            verb="GET",
            path="/test",
            length="100",
            status=501
        ))

        self.assertEqual(sink.actual.latest_access, curr_time)
        self.assertEqual(sink.actual._requests, 1)
        self.assertEqual(sink.actual._average_size, 100)
        self.assertEqual(sink.actual._errors, 1)


class SinkMock(Mock):

    def __init__(self, actual):
        super().__init__()
        self.actual = actual

    def __call__(self, data, *args, **kwargs):
        self.actual = data


if __name__ == '__main__':
    unittest.main()
