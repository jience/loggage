from typing import Dict, Optional, Type

from src.core.handlers.base import BaseStorageHandler
from src.core.handlers.mysql import MySQLStorageHandler
from src.core.handlers.elasticsearch import ElasticsearchStorageHandler


class LogStorageFactory(object):
    _handlers = {}

    @classmethod
    def register_handler(cls, name: str, handle_class: Type[BaseStorageHandler]):
        cls._handlers[name] = handle_class

    @classmethod
    def create_handler(cls, name: str, config: Dict) -> Optional[BaseStorageHandler]:
        handler_class = cls._handlers.get(name)
        if not handler_class:
            raise ValueError(f"Unsupported operation log storage handler: {name}")

        return handler_class(config)

# 注册操作日志存储处理器
LogStorageFactory.register_handler("mysql", MySQLStorageHandler)
LogStorageFactory.register_handler("elasticsearch", ElasticsearchStorageHandler)
# Add your other log handler in here.
