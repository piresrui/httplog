from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock

from httplog.Alerts import MetricSeries, Alert
from httplog.Metrics import Snapshot


class MetricSeriesTest(unittest.TestCase):
    def test_window_is_trimmed(self):
        series = MetricSeries()

        latest_access = datetime(2021, 5, 29, 16, 13, 0)
        series._snapshots = [
            datetime(2021, 5, 29, 16, 10, 0),
            datetime(2021, 5, 29, 16, 10, 30),
            datetime(2021, 5, 29, 16, 11, 0),
            datetime(2021, 5, 29, 16, 11, 30),
            datetime(2021, 5, 29, 16, 12, 0),
            datetime(2021, 5, 29, 16, 12, 30),
            datetime(2021, 5, 29, 16, 13, 0),
        ]

        snap = Snapshot()
        snap.update_latest_access(latest_access)
        series.add(snap)

        self.assertEqual(len(series._snapshots), 6)

    def test_lastest_alert_windows_correct(self):
        series = MetricSeries()
        series._snapshots = [
            datetime(2021, 5, 29, 16, 10, 0),
            datetime(2021, 5, 29, 16, 10, 30),
            datetime(2021, 5, 29, 16, 11, 0),
            datetime(2021, 5, 29, 16, 11, 30),
            datetime(2021, 5, 29, 16, 12, 0),
            datetime(2021, 5, 29, 16, 12, 30),
            datetime(2021, 5, 29, 16, 13, 0),
        ]

        rate, d = series.get_latest_alert_window(timedelta(minutes=2))
        self.assertEqual(rate, 5)


class AlertsTest(unittest.TestCase):
    def test_threshold_activated(self):
        sink = SinkMock()
        alert = Alert(0.01, timedelta(minutes=2), sink)
        alert._series = SeriesMock()

        snap = Snapshot()
        snap.update_latest_access(datetime(2021, 5, 29, 16, 13, 0))
        alert.receive(snap)

        self.assertTrue("generated" in sink.actual)


class SeriesMock(Mock):
    def get_latest_alert_window(self, d):
        return 5, timedelta(minutes=2)

    def add(self, d):
        return


class SinkMock(Mock):
    def __init__(self, actual=""):
        super().__init__()
        self.actual = actual

    def __call__(self, data, *args, **kwargs):
        self.actual = data


if __name__ == '__main__':
    unittest.main()
