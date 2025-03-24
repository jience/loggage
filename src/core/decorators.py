import functools
import json
import uuid
from typing import Callable

from src.core.models import OperationLog, OperationLogStatus
from src.core.logger import OperationLogger


def operation_logger(
        get_request: Callable,
        resource_type: str,
        action: str,
        obj_id: str = "",
        obj_name: str = "",
        ref_id: str = "",
        ref_name: str = "",
        operation_type: str = "business"
):
    """
    操作日志记录装饰器
    :param get_request: 请求上下文.
    :param resource_type: 资源类型. apps.common.constant.ResourceType
    :param action: 动作定义.如创建用户：create.apps.common.constant.OperationAction
    :param obj_id: 操作对象的id,如创建用户,obj_id为用户的UUID
    :param obj_name: 操作对象的name,如创建用户,obj_name为用户的name
    :param ref_id: 相关对象的id,如为用户设置角色,ref_id为角色的id
    :param ref_name: 相关对象的name,如为户设置角色,ref_name为角色的name
    :param operation_type: 操作日志类型. business/resource/terminal
    :return:
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            status = OperationLogStatus.SUCCESS.value
            error_code = ""
            error_message = ""
            result = None

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = OperationLogStatus.FAIL.value
                error_code = "InternalServerError"
                error_message = str(e)
                raise
            finally:
                await _log_request(
                    get_request=get_request,
                    resource_type=resource_type,
                    action=action,
                    obj_id=obj_id,
                    obj_name=obj_name,
                    ref_id=ref_id,
                    ref_name=ref_name,
                    operation_type=operation_type,
                    status=status,
                    error_code=error_code,
                    error_message=error_message
                )
        return async_wrapper
    return decorator


async def _log_request(get_request, resource_type, action, obj_id, obj_name, ref_id, ref_name,
                 operation_type, status, error_code="", error_message=""):
    try:
        request = get_request()

        # build operation log data
        log_data = {
            "request_id": _get_request_id(request),
            "user_id": _get_user_id(request),
            "user_name": _get_user_name(request),
            "obj_id": obj_id,
            "obj_name": obj_name,
            "ref_id": ref_id,
            "ref_name": ref_name,
            "resource_type": resource_type,
            "operation_type": operation_type,
            "action": action,
            "status": status,
            "detail": [],
            "request_ip": _get_request_ip(request),
            "request_params": "",
            "interval_time": 0,
            "error_code": error_code,
            "error_message": error_message,
            "extra": "",
            "response_body": "",
            "created_at": "",
            "updated_at": "",
        }

        # 创建操作日志数据模型
        log_entry = OperationLog(**log_data)

        # 获取操作日志器实例
        logger = OperationLogger.get_instance()

        # 异步记录日志
        await logger.log(log_entry)

    except Exception as e:
        print(f"Operation log request error: {str(e)}")
        pass


def _get_user_id(request) -> str:
    user_uuid = "root"
    if hasattr(request, "admin"):
        if isinstance(request.admin, str):
            request.admin = json.loads(request.admin)
        user_uuid = request.admin["userId"]
    return user_uuid

def _get_user_name(request) -> str:
    user_name = "root"
    if hasattr(request, "admin"):
        if isinstance(request.admin, str):
            request.admin = json.loads(request.admin)
        user_name = request.admin["loginName"]
    return user_name


def _get_request_ip(request):
    request_ip = "127.0.0.1"
    if getattr(request, "remote_addr"):
        if isinstance(request.remote_addr, tuple):
            request_ip = request.remote_addr[0]
        else:
            request_ip = str(request.remote_addr)
    # Reset request_ip to the ip address of client
    if hasattr(request, "client_ip"):
        request_ip = getattr(request, "client_ip")
    return request_ip


def _get_request_id(request):
    # 线程的本地属性中，是否存在request_id,在每个http请求进来时设置
    if hasattr(request, "requestId"):
        request_id = request.request_id
    else:
        # 非http请求的日志
        request_id = str(uuid.uuid4()).upper()
    return request_id
