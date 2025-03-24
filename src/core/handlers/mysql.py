import aiomysql
from typing import Dict, Any, List

from src.core.handlers.base import BaseStorageHandler
from src.core.models import OperationLog


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

                await cur.execute(query, (
                    log_data.created_at,
                    log_data.updated_at,
                    log_data.user_id,
                    log_data.user_name,
                    log_data.obj_id,
                    log_data.obj_name,
                    log_data.ref_id,
                    log_data.ref_name,
                    log_data.resource_type,
                    log_data.operation_type,
                    log_data.action,
                    log_data.status,
                    log_data.detail,
                    log_data.request_id,
                    log_data.request_ip,
                    log_data.interval_time,
                    log_data.request_params,
                    log_data.extra,
                    log_data.error_code,
                    log_data.error_message,
                    log_data.response_body
                ))
                print(cur.description)
                await conn.commit()

    async def log_batch(self, batch: List[OperationLog]) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                args = self.format_batch_insert_logs(batch)
                query = "INSERT INTO {} (created_at, updated_at, user_id, user_name, obj_id, obj_name, ref_id, ref_name, resource_type, operation_type, action, status, detail, request_id, request_ip, interval_time, request_params, extra, error_code, error_message, response_body) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.config["table"])

                await cur.executemany(query, args)
                print(cur.description)
                await conn.commit()

    async def close(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    def format_batch_insert_logs(self, batch: List[OperationLog]) -> List[tuple]:
        res = []
        for log_data in batch:
            item = (
                log_data.created_at,
                log_data.updated_at,
                log_data.user_id,
                log_data.user_name,
                log_data.obj_id,
                log_data.obj_name,
                log_data.ref_id,
                log_data.ref_name,
                log_data.resource_type,
                log_data.operation_type,
                log_data.action,
                log_data.status,
                log_data.detail,
                log_data.request_id,
                log_data.request_ip,
                log_data.interval_time,
                log_data.request_params,
                log_data.extra,
                log_data.error_code,
                log_data.error_message,
                log_data.response_body
            )
            res.append(item)
        return res
