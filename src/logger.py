
from src.base import LogStorageAdapter
from src.models import OperationLog as LogEntry


class OperationLogger:
    def __init__(self, handlers: list[LogStorageAdapter]):
        self.handlers = handlers

    def log(self, log_entry: LogEntry):
        for handler in self.handlers:
            try:
                success = handler.save(log_entry)
                if not success:
                    print(f"Save to {type(handler).__name__} error")
            except Exception as e:
                print(f"Failed to log {type(handler).__name__}: {e}")
