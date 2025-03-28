

class ConcurrentUpdateError(Exception):
    """乐观锁版本冲突异常"""
    def __init__(self, log_id: str, expected_version: int, actual_version: int):
        self.log_id = log_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"Log {log_id} version conflict: expected {expected_version}, got {actual_version}"
        )
