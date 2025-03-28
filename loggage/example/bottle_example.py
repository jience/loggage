# from gevent import monkey; monkey.patch_all()
import asyncio
import gevent

from bottle import Bottle, request, response

from loggage.core.context import OperationLogContext
from loggage.core.hybrid_logger import HybridOperationLogger
from loggage.core.logger import AsyncOperationLogger
from loggage.core.models import LogQuery
from loggage.utils.config import load_config


config = load_config("../config/config.yaml")
HybridOperationLogger().initialize(config)


app = Bottle()

@app.get("/")
def index():
    return "Bottle"


@app.get("/api/users")
@OperationLogContext(resource_type="user", action="create")
def create_user():
    setattr(request, "obj_name", "Alex")
    setattr(request, "obj_id", "123456")
    setattr(request, "ref_id", "")
    setattr(request, "ref_name", "")
    return "Hello, Bottle"

@app.get("/api/roles")
@OperationLogContext(resource_type="role", action="create")
def create_role():
    setattr(request, "obj_id", "role111111")
    setattr(request, "obj_name", "role111111")
    return "Hello, Role"


@app.get("/api/departments")
def create_department():
    job = gevent.spawn(create_dept)
    gevent.joinall([job])
    return "Hello, Dept"


def create_dept():
    with OperationLogContext(resource_type="department", action="create") as opt_logger:
        opt_logger.add_context(obj_id="dept11111111")
        opt_logger.add_context(obj_name="dept11111111")
        opt_logger.add_context(ref_id="123456")
        opt_logger.add_context(ref_name="Alex")
        opt_logger.add_context(user_id="1111")
        opt_logger.add_context(user_name="Alex")
        opt_logger.add_context(request_id="111111111111111111111111")
        opt_logger.add_context(request_ip="127.0.0.1")
        opt_logger.add_context(detail=[])


@app.get("/api/logs/<log_id>")
def get_log(log_id: str):
    loop = asyncio.get_event_loop()
    future = asyncio.run_coroutine_threadsafe(
        AsyncOperationLogger.get_instance().get_log(log_id),
        loop
    )
    log = future.result()
    if not log:
        response.status = 404
        return {"error": "Log not found"}
    return log.model_dump_json()


@app.get("/api/logs")
def query_logs():
    query_params = dict(request.query)
    page_number = int(query_params.pop("pageNumber", 1))
    page_size = min(int(query_params.pop("pageSize", 200)), 100)

    query = LogQuery(
        filters={k: v for k, v in query_params.items() if not k.startswith("search_")},
        search={k[7:]: v for k, v in query_params.items() if k.startswith("search_")},
        page_size=page_size,
        page_number=page_number,
        storage_type=request.query.get("storage")
    )

    loop = asyncio.get_event_loop()
    future = asyncio.run_coroutine_threadsafe(
        AsyncOperationLogger.get_instance().query_logs(query),
        loop,
    )

    return future.result()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
