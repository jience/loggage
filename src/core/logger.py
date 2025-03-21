import asyncio
from typing import Dict

from src.core.handlers.factory import LogStorageFactory
from src.core.models import OperationLog as OperationLogEntry


class OperationLogger:
    def __init__(self, config: Dict):
        self.default_storage = config["default_storage"]
        self.handlers = {}

        for storage_name, storage_config in config["storages"].items():
            if storage_config.get("enabled", False):
                handler = LogStorageFactory.create_handler(
                    storage_name, storage_config
                )
                if handler:
                    self.handlers[storage_name] = handler

    async def initialize(self):
        """初始化所有处理器"""
        for handler in self.handlers.values():
            if hasattr(handler, "initialize"):
                await handler.initialize()

    async def log(self, log_data: OperationLogEntry):
        tasks = []
        for handler in self.handlers.values():
            tasks.append(handler.log(log_data))
        await asyncio.gather(*tasks, return_exceptions=True)

    async def close(self):
        """关闭所有处理器连接"""
        for handler in self.handlers.values():
            await handler.close()
