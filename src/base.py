from abc import ABC, abstractmethod

from src.models import OperationLog


class LogStorageAdapter(ABC):

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def save(self, operation_log: OperationLog) -> None:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
