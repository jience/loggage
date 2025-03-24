import asyncio
from typing import Dict, List, Optional

from src.core.handlers.factory import LogStorageFactory
from src.core.models import OperationLog as OperationLogEntry


class AsyncOperationLogger:
    _instance = None  # 单例实例
    _initialized = False

    def __new__(cls, config: Optional[Dict] = None):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: Dict):
        # 监控指标扩展
        # self.metrics = {
        #     "total_logs": Counter("logger_logs_total", "Total logs processed"),
        #     "failed_logs": Counter("logger_failed_total", "Total failed logs"),
        #     "processing_time": Counter("logger_process_time", "Log processing time"),
        # }
        if not self._initialized:
            self.config = config
            self.handlers = {}
            self.loop = asyncio.get_event_loop()
            self._initialized = True
            self._init_handlers()

    def _init_handlers(self):
        """根据配置初始化处理器"""
        for storage_name, storage_config in self.config["storages"].items():
            if storage_config.get("enabled", False):
                handler = LogStorageFactory.create_handler(
                    storage_name, storage_config
                )
                if handler:
                    self.handlers[storage_name] = handler

    # @classmethod
    # def init_instance(cls, config: Dict):
    #     cls._instance = AsyncOperationLogger(config)
    #     return cls._instance
    #
    # @classmethod
    # def get_instance(cls):
    #     if cls._instance is None:
    #         raise RuntimeError("Operation Logger not initialized")
    #     return cls._instance

    async def initialize(self):
        """初始化所有处理器"""
        init_tasks = []
        for handler in self.handlers.values():
            if hasattr(handler, "initialize"):
                init_tasks.append(handler.initialize())
        await asyncio.gather(*init_tasks)

    async def log(self, log_data: OperationLogEntry):
        """异步记录单条日志"""
        tasks = []
        for handler in self.handlers.values():
            tasks.append(handler.log(log_data))
        await asyncio.gather(*tasks, return_exceptions=True)

    async def log_batch(self, batch: List[OperationLogEntry]):
        """批量记录日志"""
        batch_tasks = []
        for handler in self.handlers.values():
            if hasattr(handler, "log_batch"):
                batch_tasks.append(handler.log_batch(batch))
            else:
                # 降级为单条处理
                for log_data in batch:
                    batch_tasks.append(handler.log(log_data))
        await asyncio.gather(*batch_tasks, return_exceptions=True)

    async def close(self):
        """关闭所有处理器连接"""
        close_tasks = []
        for handler in self.handlers.values():
            close_tasks.append(handler.close())
        await asyncio.gather(*close_tasks)

    def get_metrics(self) -> Dict:
        """获取运行指标"""
        return {
            "active_handlers": len(self.handlers),
            "storage_types": list(self.handlers.keys())
        }

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
