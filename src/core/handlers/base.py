from abc import ABC, abstractmethod
from typing import List

from src.core.models import OperationLog


class BaseStorageHandler(ABC):
    @abstractmethod
    async def log(self, log_data: OperationLog) -> None:
        """异步存储日志的抽象方法"""
        pass

    @abstractmethod
    async def log_batch(self, batch: List[OperationLog]) -> None:
        """异步批量存储日志的抽象方法"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭连接资源"""
        pass
