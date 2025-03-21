from abc import ABC, abstractmethod

from src.core.models import OperationLog


class BaseStorageHandler(ABC):
    @abstractmethod
    async def log(self, log_data: OperationLog) -> None:
        """异步存储日志的抽象方法"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭连接资源"""
        pass
