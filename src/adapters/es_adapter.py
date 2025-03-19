from elasticsearch import Elasticsearch

from src.base import LogStorageAdapter
from src.models import OperationLog


class ElasticsearchStorageAdapter(LogStorageAdapter):
    def __init__(self, hosts, index):
        self.hosts = hosts
        self.index = index
        self.es = None

    def __enter__(self):
        try:
            self.es = Elasticsearch(self.hosts)
            return self
        except Exception as e:
            print(f"Connect to ES error: {str(e)}")
            raise

    def save(self, operation_log: OperationLog) -> None:
        doc = {}
        try:
            self.es.index(index=self.index, document=doc)
        except Exception as e:
            print(f"Save log to ES error: {str(e)}")
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
