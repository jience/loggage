import json
import uuid

from loggage.core.models import LogDetailItem


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

def _get_request_detail(request):
    if hasattr(request, "detail"):
        detail = [LogDetailItem(**item) for item in request.detail.get('resources', [])]
    else:
        detail = []
    return detail

def _handle_magic_param(request_obj, param):
    """
    根据模式匹配request相应的属性.
    :param request_obj: 上下文中的request对象
    :param param: 模式字符串.应该形如： obj_id\obj_name
    :return:
    """
    if not param:
        return ""
    if hasattr(request_obj, param):
        return getattr(request_obj, param)
