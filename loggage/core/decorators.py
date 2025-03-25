import functools

from loggage.core.hybrid_logger import HybridOperationLogger
from loggage.core.models import OperationLog, OperationLogStatus


def operation_logger(
        resource_type: str,
        action: str,
        operation_type: str = "business"
):
    """
    操作日志记录装饰器
    :param resource_type: 资源类型. apps.common.constant.ResourceType
    :param action: 动作定义.如创建用户：create.apps.common.constant.OperationAction
    :param operation_type: 操作日志类型. business/resource/terminal
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            status = OperationLogStatus.SUCCESS.value
            error_code = ""
            error_message = ""

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
                    operation_type=operation_type,
                    status=status,
                    error_code=error_code,
                    error_message=error_message
                )
                HybridOperationLogger().log(log_data)
        return wrapper
    return decorator


def _build_log_data(**kwargs) -> OperationLog:
    import bottle
    from loggage.core.adapters.bottle_adapter import _get_request_id
    from loggage.core.adapters.bottle_adapter import _get_user_id
    from loggage.core.adapters.bottle_adapter import _get_user_name
    from loggage.core.adapters.bottle_adapter import _get_request_ip
    from loggage.core.adapters.bottle_adapter import _get_request_detail
    from loggage.core.adapters.bottle_adapter import _handle_magic_param

    request = bottle.request
    response = bottle.response

    # build operation log data
    log_data = {
        "request_id": _get_request_id(request),
        "user_id": _get_user_id(request),
        "user_name": _get_user_name(request),
        "obj_id": _handle_magic_param(request, "obj_id"),
        "obj_name": _handle_magic_param(request, "obj_name"),
        "ref_id": _handle_magic_param(request, "ref_id"),
        "ref_name": _handle_magic_param(request, "ref_id"),
        "resource_type": kwargs.get("resource_type"),
        "operation_type": kwargs.get("operation_type"),
        "action": kwargs.get("action"),
        "status": kwargs.get("status"),
        "detail": _get_request_detail(request),
        "request_ip": _get_request_ip(request),
        "request_params": "",
        "interval_time": 0,
        "error_code": kwargs.get("error_code"),
        "error_message": kwargs.get("error_message"),
        "extra": "",
        "response_body": "",
    }

    return OperationLog(**log_data)
