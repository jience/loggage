import json
import uuid


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