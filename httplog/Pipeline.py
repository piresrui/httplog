from threading import Timer
from typing import List, Callable

from httplog.Datastore import DB
from httplog.Metrics import Snapshot
from httplog.Stage import Stage


class Pipeline(Stage[str, None]):
    """
    Wrapper object for pipeline of stages.

    Caller must ensure that:
        * First stage must consume string
        * Last stage is a sink and not a stage
        * Stages publish types that can be consumed by next stage
    """
    stages: List[Stage]
    _logger: Timer

    def __init__(self, stages: List[Callable[[Callable], Stage]]):
        super().__init__(stages[-1])
        self._logger = Timer(10, self.logger)

        self.stages = []
        current_sink = stages[-1]
        for stage in stages[-2::-1]:
            processor = stage(current_sink)
            self.stages.append(processor)
            current_sink = processor.receive

        self.stages.reverse()

    def receive(self, data: str):
        self.stages[0].receive(data)

    def start(self):
        self._logger.start()

    def end(self):
        self._logger.cancel()

    @staticmethod
    def logger():
        curr_state: Snapshot = DB.METRICS
        if curr_state:
            print("Stats:")
            print("Requests:", curr_state.requests)
            print("Requests Per Second:", curr_state.requests_per_second)
            print("Errors:", curr_state.errors)
            print("Errors Per Second:", curr_state.errors_per_second)
            print("Average Request Size:", curr_state.average_size)
            print("Verb Hits")
            for k, v in curr_state.verbs.items():
                print("\t™{} - {}".format(k, v))
            print("Section hits:")
            for k, v in curr_state.accesses.items():
                print("\t™{} - {}".format(k, v))
            print("\n\n")
