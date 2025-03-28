from typing import Union

from fastapi import  FastAPI, Request
from fastapi.responses import JSONResponse

from loggage.core.context import OperationLogContext
from loggage.core.hybrid_logger import HybridOperationLogger
from loggage.core.logger import AsyncOperationLogger
from loggage.core.models import LogQuery
from loggage.utils.config import load_config

config = load_config("../config/config.yaml")
HybridOperationLogger().initialize(config)

app = FastAPI()


def get_request():
    return Request


@app.get("/api/users")
@OperationLogContext(resource_type="User", action="create")
async def create_user():
    return JSONResponse({"hello": "FastAPI"}, status_code=200)


@app.get("/api/logs/{log_id}")
async def get_log(log_id: str, storage: Union[str, None] = None):
    log = await AsyncOperationLogger.get_instance().get_log(
        log_id
    )
    if not log:
        return {"error": "Log not found"}
    return JSONResponse(log.model_dump(mode="json"), status_code=200)


@app.get("/api/logs")
async def query_logs(
        page_number: int = 1,
        page_size: int = 20,
        storage: Union[str, None] = None
):
    page_size = min(page_size, 100)

    query = LogQuery(
        page_size=page_size,
        page_number=page_number,
        storage_type=storage
    )

    result = await AsyncOperationLogger.get_instance().query_logs(query)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="0.0.0.0", port=8080)
