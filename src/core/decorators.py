import functools

from src.core.hybrid_logger import HybridLogger
from src.core.models import OperationLog, OperationLogStatus


def hybrid_logger(
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
    :param resource_type: 资源类型. apps.common.constant.ResourceType
    :param action: 动作定义.如创建用户：create.apps.common.constant.OperationAction
    :param obj_id: 操作对象的id,如创建用户,obj_id为用户的UUID
    :param obj_name: 操作对象的name,如创建用户,obj_name为用户的name
    :param ref_id: 相关对象的id,如为用户设置角色,ref_id为角色的id
    :param ref_name: 相关对象的name,如为户设置角色,ref_name为角色的name
    :param operation_type: 操作日志类型. business/resource/terminal
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            status = OperationLogStatus.SUCCESS.value
            error_code = ""
            error_message = ""
            result = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = OperationLogStatus.FAIL.value
                error_code = "InternalServerError"
                error_message = str(e)
                raise
            finally:
                log_data = _build_log_data(
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
                HybridLogger().log(log_data)
        return wrapper
    return decorator


def _build_log_data(**kwargs) -> OperationLog:
    import bottle
    from src.core.adapters.bottle_adapter import _get_request_id
    from src.core.adapters.bottle_adapter import _get_user_id
    from src.core.adapters.bottle_adapter import _get_user_name
    from src.core.adapters.bottle_adapter import _get_request_ip

    request = bottle.request
    response = bottle.response

    # build operation log data
    log_data = {
        "request_id": _get_request_id(request),
        "user_id": _get_user_id(request),
        "user_name": _get_user_name(request),
        "obj_id": kwargs.get("obj_id"),
        "obj_name": kwargs.get("obj_name"),
        "ref_id": kwargs.get("ref_id"),
        "ref_name": kwargs.get("ref_id"),
        "resource_type": kwargs.get("resource_type"),
        "operation_type": kwargs.get("operation_type"),
        "action": kwargs.get("action"),
        "status": kwargs.get("status"),
        "detail": [],
        "request_ip": _get_request_ip(request),
        "request_params": "",
        "interval_time": 0,
        "error_code": kwargs.get("error_code"),
        "error_message": kwargs.get("error_message"),
        "extra": "",
        "response_body": "",
    }

    return OperationLog(**log_data)
