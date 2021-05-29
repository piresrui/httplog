from copy import deepcopy
from datetime import datetime, timedelta
from collections import Counter
from typing import Callable, Optional

from httplog.Datastore import DB
from httplog.Stage import Stage


class Data:
    """
    Wrapper class to hold parsed log data
    """

    def __init__(self, host: str, rfc981: str, user: str, date: datetime, verb: str, path: str, length: str,
                 status: int):
        self.host = host
        self.rfc981 = rfc981
        self.user = user
        self.date = date
        self.verb = verb
        self.path = path
        self.length = length
        self.status = status


class Snapshot:
    """
    Snapshot state of metrics
    """
    _latest_access: Optional[datetime]
    _duration: timedelta
    _requests: int
    _requests_per_second: float
    _errors: int
    _errors_per_second: float
    _average_size: float
    _total_size: int
    _accesses: Counter
    _verb_count: Counter

    def __init__(self):
        self._latest_access = None
        self._duration = timedelta()
        self._requests = 0
        self._requests_per_second = 0
        self._errors = 0
        self._errors_per_second = 0
        self._total_size = 0
        self._average_size = 0
        self._accesses = Counter()
        self._verb_count = Counter()

    def update_latest_access(self, access_time: datetime):
        """
        Updates latest access and duration of metrics.
        Should **ALWAYS** be called first.

        :param access_time: Latest access time
        """
        if self._latest_access is None:
            self._duration = timedelta(seconds=1)
        elif access_time == self._latest_access:
            self._duration = timedelta(seconds=1)
        elif access_time < self._latest_access:
            self._duration = self._latest_access - access_time
        else:
            self._duration = access_time - self._latest_access
        self._latest_access = access_time

    def inc_requests(self):
        """
        Increments number of accesses by one.
        """
        self._requests += 1
        self._requests_per_second = self._requests / self._duration.total_seconds()

    def inc_errors(self):
        """
        Increments errors by one.
        """
        self._errors += 1
        self._errors_per_second = self._errors / self._duration.total_seconds()

    def inc_size(self, size: int):
        """
        Increments total size of requests in a metric window.

        :param size: Length of last request
        """
        self._total_size += size
        self._average_size = self._total_size / self._requests

    def inc_accesses(self, path: str):
        """
        Increments accesses to a given path by one.

        :param path: Path to increment
        """
        self._accesses.update({path: 1})

    def inc_verb(self, verb: str):
        self._verb_count.update({verb: 1})

    @property
    def latest_access(self) -> datetime:
        return self._latest_access

    @property
    def accesses(self) -> Counter:
        return self._accesses

    @property
    def verbs(self) -> Counter:
        return self._verb_count

    @property
    def requests(self) -> int:
        return self._requests

    @property
    def requests_per_second(self) -> float:
        return self._requests_per_second

    @property
    def errors(self) -> int:
        return self._errors

    @property
    def errors_per_second(self) -> float:
        return self._errors_per_second

    @property
    def average_size(self) -> float:
        return self._average_size


class Metrics(Stage[Data, Snapshot]):
    """
    Metrics stage.
    Updates current state of metrics and published a copy of current state
    """

    def __init__(self, sink: Callable[[Snapshot], None]):
        super().__init__(sink)
        self._SNAPSHOT = Snapshot()

    def receive(self, data: Data):
        self._SNAPSHOT.update_latest_access(data.date)
        self._SNAPSHOT.inc_accesses(data.path)
        self._SNAPSHOT.inc_verb(data.verb)
        self._SNAPSHOT.inc_requests()
        self._SNAPSHOT.inc_size(int(data.length))

        if data.status > 400:
            self._SNAPSHOT.inc_errors()

        copy_snapshot = deepcopy(self._SNAPSHOT)
        self.publish(copy_snapshot)
        # Update database
        DB.METRICS = copy_snapshot
