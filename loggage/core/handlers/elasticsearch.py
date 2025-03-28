from typing import Dict, Any, List, Iterator, Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from elasticsearch.exceptions import NotFoundError

from loggage.core.exceptions import ConcurrentUpdateError
from loggage.core.handlers.base import BaseStorageHandler
from loggage.core.models import OperationLog


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

    async def get_log(self, log_id: str) -> Optional[OperationLog]:
        try:
            resp = await self.client.get(
                index=self.index,
                id=log_id
            )
            return OperationLog(**resp["_source"]["docs"])
        except NotFoundError:
            return None

    async def query_logs(
        self,
        filters: Dict = None,
        search: Dict = None,
        sort: List[tuple] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> (List[OperationLog], int):
        query = {"bool": {"must": []}}

        # 精准过滤
        if filters:
            for field, value in filters.items():
                query["bool"]["must"].append(
                    {"term": {field: value}}
                )

        # 模糊匹配
        if search:
            for field, keyword in search.items():
                query["bool"]["must"].append(
                    {"wildcard": {field: f"*{keyword}*"}}
                )

        # 排序规则
        sort_rules = []
        if sort:
            for field, direction in sort:
                sort_rules.append({field: {"order": direction}})

        body = {"query": query, "sort": sort_rules, "from": offset, "size": limit}

        # 执行查询
        resp = await self.client.search(
            index=self.index,
            body=body
        )

        total = resp["hits"]["total"]["value"]
        results = [OperationLog(**hit["_source"]) for hit in resp["hits"]["hits"]]

        return results, total

    async def update_log(self, log_id: str, updates: dict) -> bool:
        try:
            doc = await self.client.get(
                index=self.index,
                id=log_id
            )
            current_version = doc["_version"]

            if updates.get("version") != current_version + 1:
                raise ConcurrentUpdateError(
                    log_id=log_id,
                    expected_version=current_version + 1,
                    actual_version=current_version
                )

            response = await self.client.update(
                index=self.index,
                id=log_id,
                body={"doc": updates},
                # version=current_version
            )
            return response["result"] == "updated"
        except NotFoundError:
            return False

    def _generate_data(self, batch: List[OperationLog]) -> Iterator:
        for log_data in batch:
            yield {
                "_index": self.index,
                "_source": log_data.model_dump(mode="json")
            }

    async def close(self) -> None:
        await self.client.close()
