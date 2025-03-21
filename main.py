import asyncio
import uuid
from datetime import datetime

from core.logger import OperationLogger
from core.models import OperationLog, LogDetailItem
from utils.config import load_config


async def main():
    config = load_config("config/config.yaml")
    operation_logger = OperationLogger(config)
    await operation_logger.initialize()

    log_detail = LogDetailItem(id=uuid.uuid4().hex, name="vdi", type="admin")
    log_data = OperationLog(
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
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    try:
        await operation_logger.log(log_data)
    finally:
        await operation_logger.close()

if __name__ == "__main__":
    asyncio.run(main())
