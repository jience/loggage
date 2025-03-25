import json

import aiomysql
from typing import Dict, Any, List

from loggage.core.handlers.base import BaseStorageHandler
from loggage.core.models import OperationLog


class MySQLStorageHandler(BaseStorageHandler):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pool = None

    async def initialize(self):
        """初始化连接池"""
        self.pool = await aiomysql.create_pool(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            db=self.config["db"],
            minsize=1,
            maxsize=self.config["pool_size"]
        )

    async def log(self, log_data: OperationLog) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = "INSERT INTO {} (created_at, updated_at, user_id, user_name, obj_id, obj_name, ref_id, ref_name, resource_type, operation_type, action, status, detail, request_id, request_ip, interval_time, request_params, extra, error_code, error_message, response_body) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.config["table"])

                await cur.execute(query, self._format_log_data_sql_value(log_data))
                print(cur.description)
                await conn.commit()

    async def log_batch(self, batch: List[OperationLog]) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                logs_list = [self._format_log_data_sql_value(log_data) for log_data in batch]
                query = "INSERT INTO {} (created_at, updated_at, user_id, user_name, obj_id, obj_name, ref_id, ref_name, resource_type, operation_type, action, status, detail, request_id, request_ip, interval_time, request_params, extra, error_code, error_message, response_body) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.config["table"])

                await cur.executemany(query, logs_list)
                print(cur.description)
                await conn.commit()

    async def close(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    @staticmethod
    def _format_log_data_sql_value(log_data: OperationLog) -> tuple:
        log_data_dict = log_data.model_dump(mode="json")
        log_data_dict["detail"] = json.dumps(log_data_dict["detail"])
        return (
            log_data_dict.get("created_at"),
            log_data_dict.get("updated_at"),
            log_data_dict.get("user_id"),
            log_data_dict.get("user_name"),
            log_data_dict.get("obj_id"),
            log_data_dict.get("obj_name"),
            log_data_dict.get("ref_id"),
            log_data_dict.get("ref_name"),
            log_data_dict.get("resource_type"),
            log_data_dict.get("operation_type"),
            log_data_dict.get("action"),
            log_data_dict.get("status"),
            log_data_dict.get("detail"),
            log_data_dict.get("request_id"),
            log_data_dict.get("request_ip"),
            log_data_dict.get("interval_time"),
            log_data_dict.get("request_params"),
            log_data_dict.get("extra"),
            log_data_dict.get("error_code"),
            log_data_dict.get("error_message"),
            log_data_dict.get("response_body")
        )
