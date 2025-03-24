import asyncio
import queue
import threading
import time
from typing import Dict, List

from src.core.logger import AsyncOperationLogger
from src.core.models import OperationLog


class HybridLogger:
    _instance = None
    BATCH_SIZE = 100
    MAX_QUEUE_SIZE = 10000

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._init_flag = False
        return cls._instance

    def __init__(self):
        pass
        # self.metrics = {
        #     "queue_size": Gauge("log_queue_size", "Current queue size"),
        #     "processed_total": Counter("log_processed", "Total processed logs"),
        #     "failed_total": Counter("logs_failed", "Total failed logs")
        # }

    def initialize(self, config: Dict):
        if not self._init_flag:
            self.config = config
            self.queue = queue.Queue(maxsize=self.MAX_QUEUE_SIZE)
            self.event_loop = None
            self.consumer_thread = None
            self._running = False
            self._init_flag = True

            self._start_consumer()

    def _start_consumer(self):
        def consumer_worker():
            # 初始化事件循环
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)

            # 初始化日志器
            self.async_logger = AsyncOperationLogger(self.config)
            self.event_loop.run_until_complete(self.async_logger.initialize())

            # 启动批处理任务
            self._running = True
            while self._running or not self.queue.empty():
                self.event_loop.run_until_complete(self._process_batch())
                time.sleep(0.1)  # 降低CPU占用

            # 关闭资源
            self.event_loop.run_until_complete(self.async_logger.close())
            self.event_loop.close()

        self.consumer_thread = threading.Thread(
            target=consumer_worker,
            daemon=True,
            name="LogConsumer"
        )
        self.consumer_thread.start()

    async def _process_batch(self):
        """批量处理队列中的日志"""
        # self.metrics["queue_size"].set(self.queue.qsize())
        batch = []
        try:
            # 批量获取日志
            while len(batch) < self.BATCH_SIZE:
                item = self.queue.get_nowait()
                batch.append(item)
        except queue.Empty:
            pass

        if batch:
            try:
                await self.async_logger.log_batch(batch)
                # self.metrics["processed_total"].inc(len(batch))
            except Exception as e:
                # self.metrics["failed_total"].inc(len(batch))
                await self._handle_failed_batch(batch)

    async def _handle_failed_batch(self, batch: List[OperationLog]):
        """失败批次处理"""
        retry_queue = []
        for log in batch:
            if log.retry_count < 3:
                log.retry_count += 1
                retry_queue.append(log)
            else:
                await self._send_to_dead_letter(log)

        if retry_queue:
            self.queue.queue.extendleft(retry_queue)

    async def _send_to_dead_letter(self, log_data: OperationLog):
        """死信队列处理"""
        pass

    def log(self, log_data: OperationLog):
        """线程安全的日志提交"""
        try:
            self.queue.put_nowait(log_data)
        except queue.Full:
            self._handle_queue_full(log_data)

    def _handle_queue_full(self, log_data: OperationLog):
        """队列满处理策略"""
        # 1. 丢弃最旧日志
        try:
            self.queue.get_nowait()
            self.queue.put_nowait(log_data)
        except queue.Empty:
            pass

    def shutdown(self):
        """优雅关闭"""
        self._running = False
        if self.consumer_thread:
            self.consumer_thread.join(timeout=30)
