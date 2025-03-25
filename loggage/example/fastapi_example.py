from fastapi import  FastAPI, Request
from fastapi.responses import JSONResponse

from loggage.core.decorators import operation_logger
from loggage.core.hybrid_logger import HybridOperationLogger
from loggage.utils.config import load_config

config = load_config("../config/config.yaml")
HybridOperationLogger().initialize(config)

app = FastAPI()


def get_request():
    return Request


@app.get("/api/users")
@operation_logger(resource_type="User", action="create")
async def create_user():
    return JSONResponse({"hello": "FastAPI"}, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="0.0.0.0", port=8080)
