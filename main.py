import asyncio
from datetime import datetime

from core.logger import OperationLogger
from core.models import OperationLog, LogDetailItem
from utils.config import load_config
from utils.tools import generate_uuid_str


async def main():
    config = load_config("config/config.yaml")
    operation_logger = OperationLogger(config)
    await operation_logger.initialize()

    log_detail = LogDetailItem(id=generate_uuid_str(), name="vdi", type="admin")
    log_data = OperationLog(
        request_id=generate_uuid_str(),
        user_id=generate_uuid_str(),
        user_name="vdi",
        obj_id=generate_uuid_str(),
        obj_name="Client-W",
        ref_id=generate_uuid_str(),
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
