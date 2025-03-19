import uuid
import yaml

from src.factory import LogStorageFactory
from src.logger import OperationLogger
from src.models import LogDetailItem, OperationLog as LogEntry


def load_config(file_path):
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)
    return config


if __name__ == "__main__":
    config_file = "config.yaml"
    config = load_config(config_file)
    handlers = []

    for storage_config in config["storages"]:
        with LogStorageFactory.create_handler(storage_config) as handler:
            handlers.append(handler)

    logger = OperationLogger(handlers)

    log_detail = LogDetailItem(
        id=uuid.uuid4().hex,
        name="vdi",
        type="admin"
    )

    log_entry = LogEntry(
        request_id=uuid.uuid4().hex,
        user_id=uuid.uuid4().hex,
        user_name="vdi",
        obj_id=uuid.uuid4().hex,
        obj_name="Arclient-W",
        ref_id=uuid.uuid4().hex,
        ref_name="abc",
        resource_type="user",
        operation_type="business",
        action="login",
        status="success",
        detail=[log_detail],
        request_ip="127.0.0.1",
        request_params="{}",
        interval_time=0,
        error_code="",
        error_message="",
        extra="{}",
        response_body="{}",
        created_at="2025-03-19 16:58:00",
        updated_at="2025-03-19 16:58:00"
    )

    logger.log(log_entry)
