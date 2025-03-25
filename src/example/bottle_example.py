from bottle import Bottle

from src.core.decorators import operation_logger
from src.core.hybrid_logger import HybridOperationLogger
from src.utils.config import load_config


config = load_config("/home/zalex/PycharmProjects/loggage/config/config.yaml")
HybridOperationLogger().initialize(config)


app = Bottle()

@app.get("/")
def index():
    return "Bottle"


@app.get("/api/users")
@operation_logger(resource_type="user", action="create",
                  obj_id="123", obj_name="user123",
                  ref_id="456", ref_name="456")
def create_user():
    return "Hello, Bottle"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
