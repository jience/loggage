
from src.base import LogStorageAdapter
from src.adapters.mysql_adapter import MySQLStorageAdapter
from src.adapters.es_adapter import ElasticsearchStorageAdapter


class LogStorageFactory(object):
    handlers = {
        "mysql": MySQLStorageAdapter,
        "elasticsearch": ElasticsearchStorageAdapter,
    }

    @classmethod
    def register_handler(cls, name, handle_class):
        cls.handlers[name] = handle_class

    @classmethod
    def create_handler(cls, config: dict) -> LogStorageAdapter:
        handler_type = config.get("type")
        if handler_type not in cls.handlers:
            raise ValueError(f"Unsupported log handler: {handler_type}")

        handler_class = cls.handlers[handler_type]
        return handler_class(**config["params"])
