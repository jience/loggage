from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from loggage.core.models import OperationLog


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
    async def get_log(self, log_id: str) -> Optional[OperationLog]:
        pass

    @abstractmethod
    async def query_logs(
            self,
            filters: Dict = None,
            search: Dict = None,
            sort: List[tuple] = None,
            offset: int = 0,
            limit: int = 20
    ) -> (List[OperationLog], int):
        pass

    @abstractmethod
    async def update_log(self, log_id: str, updates: dict) -> bool:
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭连接资源"""
        pass
