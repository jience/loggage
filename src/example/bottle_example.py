import asyncio
from bottle import Bottle, request

from src.core.decorators import operation_logger
from src.core.logger import OperationLogger
from src.utils.config import load_config


config = load_config("/home/zalex/PycharmProjects/loggage/config/config.yaml")
op_logger = OperationLogger(config)
asyncio.run(op_logger.initialize())

app = Bottle()


def get_request():
    return request

@app.get("/")
def index():
    return "Bottle"


@app.get("/api/users")
@operation_logger(get_request, resource_type="User", action="create", obj_id="123", obj_name="user123",
                  ref_id="456", ref_name="456")
def create_user():
    return "Hello, Bottle"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
