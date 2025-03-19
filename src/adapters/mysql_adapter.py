import pymysql
from pymysql.err import Error

from src.base import LogStorageAdapter
from src.models import OperationLog


class MySQLStorageAdapter(LogStorageAdapter):
    def __init__(self, host, user, password, database, table, **kwargs):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        self.table = table
        self.connection = None

    def __enter__(self):
        try:
            self.connection = pymysql.connect(**self.config)
            return self
        except Error as e:
            print(f"Connect to MySQL error: {str(e)}")
            raise

    def save(self, operation_log: OperationLog) -> bool:
        insert_sql = f"INSERT INTO {self.table} () VALUES ()"

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_sql, ())
                self.connection.commit()
                return True
        except Error as e:
            print(f"Failed to save log in mysql: {e}")
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
