import queue
import threading
from concurrent.futures import ThreadPoolExecutor

from src.core.models import OperationLog as LogEntry


class AsyncLogQueue(object):
    def __init__(self, max_size=10000, retries=3):
        self.queue = queue.Queue(maxsize=max_size)
        self.retries = retries
        self._stop_event = threading.Event()

        # Init thread pool
        self.worker_pool = ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix="LogWorker"
        )

    def put(self, log_entry: LogEntry):
        try:
            self.queue.put_nowait((log_entry, 0))
            return True
        except queue.Full:
            print(f"Warn: queue full!!!")
            return False

    def start_consumers(self, logger="AsyncOperationLogger"):
        def _worker():
            while not self._stop_event.isSet():
                try:
                    entry, retry_count = self.queue.get(timeout=1)
                    success = self._process_entry(entry, logger)

                    if not success and retry_count < self.retries:
                        self.queue.put((entry, retry_count + 1))
                except queue.Empty:
                    continue

        for _ in range(4):
            self.worker_pool.submit(_worker)

    def _process_entry(self, entry: LogEntry, logger="AsyncOperationLogger") -> bool:
        try:
            return logger._sync_log(entry)
        except Exception as e:
            print(f"Failed to log: {e}")
            return False

    def graceful_shutdown(self):
        self._stop_event.set()
        self.worker_pool.shutdown(wait=True, cancel_futures=False)

        while not self.queue.empty():
            entry, _ = self.queue.get()
            self._process_entry(entry)