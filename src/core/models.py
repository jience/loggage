from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OperationLogStatus(Enum):
    SUCCESS = "success"
    FAIL = "fail"


class LogDetailItem(BaseModel):
    id: str    # 操作对象ID
    name: str  # 操作对象名称
    type: str  # 操作对象类型


class OperationLog(BaseModel):
    request_id: str                             # 请求ID
    user_id: str                                # 操作者ID
    user_name: str                              # 操作者名称
    obj_id: str                                 # 操作对象ID
    obj_name: str                               # 操作对象名称
    ref_id: Optional[str] = None                # 关联对象ID
    ref_name: Optional[str] = None              # 关联对象名称
    resource_type: str                          # 资源对象类型
    operation_type: str                         # 操作日志类型
    action: str                                 # 操作动作
    status: str                                 # 日志状态
    detail: List[LogDetailItem]                 # 操作对象详情
    request_ip: str                             # 请求IP
    request_params: Optional[str] = None        # 请求参数
    interval_time: int                          # 操作时长
    error_code: Optional[str] = None            # 操作失败错误码
    error_message: Optional[str] = None         # 操作失败详情信息
    extra: Optional[str] = None                 # 其他信息
    response_body: Optional[str] = None         # 响应体
    created_at: datetime = Field(default_factory=datetime.now)    # 创建时间
    updated_at: datetime = Field(default_factory=datetime.now)    # 更新时间
    retry_count: int = 0                        # 重试计数器
