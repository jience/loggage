from typing import Dict, Any

from elasticsearch import AsyncElasticsearch

from src.core.handlers.base import BaseStorageHandler
from src.core.models import OperationLog


class ElasticsearchStorageHandler(BaseStorageHandler):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = AsyncElasticsearch(
            hosts=self.config["hosts"],
            request_timeout=self.config.get("timeout", 30)
        )
        self.index = config["index"]

    async def log(self, log_data: OperationLog) -> None:
        doc = log_data.model_dump()
        await self.client.index(
            index=self.index,
            document=doc
        )

    async def close(self) -> None:
        await self.client.close()
