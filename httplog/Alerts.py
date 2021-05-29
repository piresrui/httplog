from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Callable

from httplog.Metrics import Snapshot
from httplog.Stage import Stage


class MetricSeries:
    """
    Wrapper for an Alert Window.
    """
    _snapshots: List[datetime]
    _duration: timedelta

    def __init__(self):
        self._snapshots = []
        self._duration = timedelta(minutes=2)

    def add(self, snapshot: Snapshot):
        """
        Adds a new snapshot to the alert window.
        Sorts window by date, and clears window of snapshots older than window size.

        :param snapshot: New snapshot
        """
        self._snapshots.append(snapshot.latest_access)
        self._snapshots.sort()

        # Find earliest entry within duration
        start = 0
        for i, snapshot in enumerate(self._snapshots):
            start = i
            if (self._snapshots[-1] - snapshot) <= self._duration:
                break

        # Trim list of snapshots to only latest alert window
        if (self._snapshots[-1] - self._snapshots[start]) >= self._duration:
            self._snapshots = self._snapshots[start:]

    def get_latest_alert_window(self, period: timedelta) -> Tuple[int, Optional[datetime]]:
        """
        Returns number of requests in the lastest window and the latest access.

        :param period: Time period window
        :return: request in window, latest access
        """
        if len(self._snapshots) < 2:
            return 0, None

        hits = sum(map(lambda t: (self._snapshots[-1] - t) <= period, self._snapshots))
        return hits, self._snapshots[-1]


class Alert(Stage[Snapshot, str]):
    """
    Keeps track of current state of metrics and alerts when thresholds are crossed.
    """
    _series: MetricSeries
    _period: timedelta
    _threshold: float
    _in_alert = False
    _alert_message = "High traffic generated an alert - hits = {}, triggered at {}"
    _recovery_message = "Recovered from previous alert - triggered at {}"

    def __init__(self, threshold: float, period: timedelta, sink: Callable[[str], None]):
        super().__init__(sink)
        self._period = period
        self._threshold = threshold
        self._series = MetricSeries()

    def receive(self, data: Snapshot):
        self._series.add(data)
        requests, last = self._series.get_latest_alert_window(self._period)

        if requests == 0:
            return

        rate = requests / self._period.total_seconds()
        if rate >= self._threshold and not self._in_alert:
            self._in_alert = True
            self.publish(self._alert_message.format(rate, last))
        elif self._in_alert and rate < self._threshold:
            self._in_alert = False
            self.publish(self._recovery_message.format(last))
