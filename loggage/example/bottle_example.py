from bottle import Bottle, request

from loggage.core.decorators import operation_logger
from loggage.core.hybrid_logger import HybridOperationLogger
from loggage.utils.config import load_config


config = load_config("../config/config.yaml")
HybridOperationLogger().initialize(config)


app = Bottle()

@app.get("/")
def index():
    return "Bottle"


@app.get("/api/users")
@operation_logger(resource_type="user", action="create")
def create_user():
    setattr(request, "obj_name", "Alex")
    setattr(request, "obj_id", "123456")
    setattr(request, "ref_id", "")
    setattr(request, "ref_name", "")
    return "Hello, Bottle"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
