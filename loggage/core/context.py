import uuid
from contextlib import ContextDecorator
from functools import wraps
from typing import Callable

from loggage.core.models import LogDetailItem, OperationLog
from loggage.core.hybrid_logger import HybridOperationLogger


class OperationLogContext(ContextDecorator):
    def __init__(
            self,
            resource_type: str,
            action: str,
            operation_type: str = "business"
    ):
        """
        操作日志上下文管理器

        :param resource_type: 资源类型. apps.common.constant.ResourceType
        :param action: 动作定义. 如创建用户：create.apps.common.constant.OperationAction
        :param operation_type: 操作日志类型. business/resource/terminal
        """
        self.resource_type = resource_type
        self.action = action
        self.operation_type = operation_type
        self.context = {}
        self.status = ""
        self.error_code = ""
        self.error_message = ""

    def __enter__(self):
        return self

    async def __aenter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            from bottle import request
            print(request.method)
            self.context.update({
                "request_id": self._get_request_id(request),
                "request_ip": self._get_request_ip(request),
                "user_id": self._get_user_id(request),
                "user_name": self._get_user_name(request),
                "detail": self._get_request_detail(request),
                "ref_id": self._handle_magic_param(request, "ref_id"),
                "ref_name": self._handle_magic_param(request, "ref_name"),
                "obj_id": self._handle_magic_param(request, "obj_id"),
                "obj_name": self._handle_magic_param(request, "obj_name")
            })
        except RuntimeError:
            pass

        if exc_type:
            self.status = "fail"
            self.error_message = str(exc_val.error_message if hasattr(exc_val, "error_message") else "")
            self.error_code = str(exc_val.error_code if hasattr(exc_val, "error_code") else "")
        else:
            self.status = "success"

        # todo: log
        HybridOperationLogger().log(self._generate_log_data())

        return False

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_context(self, **kwargs):
        self.context.update(kwargs)

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper

    def _generate_log_data(self) -> OperationLog:
        return OperationLog(
            request_id=self.context["request_id"],
            user_id=self.context["user_id"],
            user_name=self.context["user_name"],
            obj_id=self.context["obj_id"],
            obj_name=self.context["obj_name"],
            ref_id=self.context["ref_id"],
            ref_name=self.context["ref_name"],
            resource_type=self.resource_type,
            operation_type=self.operation_type,
            action=self.action,
            status=self.status,
            detail=self.context["detail"],
            request_ip="127.0.0.1",
            request_params="",
            interval_time=0,
            error_code="",
            error_message="",
            extra="",
            response_body="",
        )

    @staticmethod
    def _get_user_id(request_obj) -> str:
        user_uuid = "root"
        if hasattr(request_obj, "admin"):
            user_uuid = request_obj.admin["userId"]
        return user_uuid

    @staticmethod
    def _get_user_name(request_obj) -> str:
        user_name = "root"
        if hasattr(request_obj, "admin"):
            user_name = request_obj.admin["loginName"]
        return user_name

    @staticmethod
    def _get_request_ip(request_obj):
        request_ip = "127.0.0.1"
        if getattr(request_obj, "remote_addr"):
            if isinstance(request_obj.remote_addr, tuple):
                request_ip = request_obj.remote_addr[0]
            else:
                request_ip = str(request_obj.remote_addr)
        # Reset request_ip to the ip address of client
        if hasattr(request_obj, "client_ip"):
            request_ip = getattr(request_obj, "client_ip")
        return request_ip

    @staticmethod
    def _get_request_id(request_obj):
        # 线程的本地属性中，是否存在request_id,在每个http请求进来时设置
        if hasattr(request_obj, "requestId"):
            request_id = request_obj.request_id
        else:
            # 非http请求的日志
            request_id = str(uuid.uuid4()).upper()
        return request_id

    @staticmethod
    def _get_request_detail(request_obj):
        if hasattr(request_obj, "detail"):
            detail = [
                LogDetailItem(**item) for item in request_obj.detail.get("resources", [])
            ]
        else:
            detail = []
        return detail

    @staticmethod
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
            return getattr(request_obj, param, "")
