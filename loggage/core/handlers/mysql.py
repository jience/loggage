import json

import aiomysql
from typing import Dict, Any, List, Optional

from loggage.core.exceptions import ConcurrentUpdateError
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

    async def get_log(self, log_id: str) -> Optional[OperationLog]:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM {table_name} WHERE id = %s".format(table_name=self.config["table"]),
                    (log_id, )
                )
                result = await cur.fetchone()
                return OperationLog(**dict(result)) if result else None

    async def query_logs(
        self,
        filters: Dict = None,
        search: Dict = None,
        sort: List[tuple] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> (List[OperationLog], int):
        # 构建查询条件
        where_clauses = []
        params = []

        # 精准过滤
        if filters:
            for field, value in filters.items():
                where_clauses.append(f"{field} = %s")
                params.append(value)

        # 模糊匹配
        if search:
            for field, keyword in search.items():
                where_clauses.append(f"{field} LIKE %s")
                params.append(f"%{keyword}%")

        # 排序规则
        order_by = "ORDER BY " + ", ".join(
            [f"{field} {direction}" for field, direction in sort]
        ) if sort else ""

        # 分页
        limit_clause = "LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        # 执行查询
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 查询数据
                query = f"""
                    SELECT * FROM {self.config["table"]}
                    {'WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''}
                    {order_by}
                    {limit_clause}
                """
                await cur.execute(query, params)
                results = await cur.fetchall()

                # 查询总数
                count_query = f"""
                    SELECT COUNT(*) FROM {self.config["table"]}
                    {'WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''}
                """
                await cur.execute(count_query, params[:-2])  # 排除分页参数
                total = await cur.fetchone()

        return [OperationLog(**dict(r)) for r in results], total[0]

    async def update_log(self, log_id: str, updates: dict) -> bool:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                if "version" not in updates:
                    raise ValueError("Version field is required for update")

                # 构建乐观锁更新语句
                set_clause = ", ".join([
                    f"{field} = %s"
                    for field in updates.keys()
                ])
                values = list(updates.values()) + [log_id, updates["version"]-1]

                query = f"""
                    UPDATE {self.config["table"]}
                    SET {set_clause}, version = version + 1
                    WHERE log_id = %s AND version = %s
                """
                await cur.execute(query, values)
                await conn.commit()

                if cur.rowcount == 0:
                    await cur.execute(
                        f"""SELECT version FROM {self.config["table"]} WHERE log_id = %s""",
                        (log_id,)
                    )
                    result = await cur.fetchone()
                    actual_version = result[0] if result else None
                    raise ConcurrentUpdateError(
                        log_id=log_id,
                        expected_version=updates["version"],
                        actual_version=actual_version
                    )
                return True

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
