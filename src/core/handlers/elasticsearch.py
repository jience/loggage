from typing import Dict, Any, List, Iterator

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

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

    async def log_batch(self, batch: List[OperationLog]) -> None:
        await async_bulk(self.client, self._generate_data(batch))

    def _generate_data(self, batch: List[OperationLog]) -> Iterator:
        for log_data in batch:
            yield {
                "_index": self.index,
                "docs": log_data.model_dump(mode="json")
            }

    async def close(self) -> None:
        await self.client.close()
