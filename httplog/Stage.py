from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Generic

T = TypeVar("T")  # Input type
K = TypeVar("K")  # Output type


class Stage(ABC, Generic[T, K]):
    """
    Abstract class for a pipeline stage.
    """
    sink: Callable[[K], None]

    def __init__(self, sink: Callable[[K], None]):
        """
        :param sink: Sink to publish data to
        """
        self.sink = sink

    @abstractmethod
    def receive(self, data: T):
        """
        Receive and process data. Should call publish when done processing

        :param data: data to process
        """
        pass

    def publish(self, data: K):
        """
        Emits data to sink

        :param data: Data to publish
        """
        self.sink(data)
