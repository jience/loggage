<a name="readme-top"></a>

<div align="center">
  <img src="./loggage.png" align="center" width="441" alt="Project icon">
  <h3 align="center">Loggage: easy and happy</h3>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/uv-32173c?logo=uv&logoColor=fff">
  <img src="https://img.shields.io/badge/Ruff-6340ac?logo=Ruff&logoColor=fff">
  <img src="https://img.shields.io/badge/Python-3.10-34D058">
  <p align="center">
    中文 | <a href="README.md">English</a>
  </p>
</div>

# 介绍

`Loggage`是一款记录操作日志的通用组件，它旨在帮助您通过装饰器或者调用普通函数的方式记录业务系统的操作日志，对业务代码无侵入。同时允许您根据自己的项目需求，将操作日志存储到不同的存储位置，支持MySQL、Elasticsearch以及Redis等。

## 主要特性

- **完全异步**： 安全支持async/await异步体系
- **异常安全**： 日志记录失败不会影响API正常流程
- **类型安全**： 基于pydantic模型进行数据验证
- **高性能**： 日志记录完全异步执行
- **扩展便捷**： 工厂模式+标准接口方便新增存储处理器
- **配置驱动**： 通过YAML配置灵活控制存储方式

## 安装

1. 安装 uv（一个快速的 Python 包管理器）:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 克隆仓库:

```bash
git clone https://github.com/jience/loggage.git
cd loggage
```

3. 创建并激活虚拟环境:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# Or on Windows:
# .venv\Scripts\activate
```

4. 安装依赖:

```bash
uv pip install -r requirements.txt
```

## 配置说明

Follow these steps to set up your configuration:

1. Create a `config.yaml` file in the `config` directory (you can copy from the example):

```bash
cp config/config.example.yaml config/config.yaml
```

2. 编辑 `config/config.yaml` 添加自定义配置:

```yaml
default_storage: mysql
storages:
  mysql:
    enabled: true
    host: localhost
    port: 3306
    user: user
    password: password
    db: db_name
    table: operation_log
    pool_size: 20
    max_overflow: 5

  elasticsearch:
    enabled: true
    hosts: ["http://localhost:9200"]
    index: operation-log
    timeout: 30

  redis:
    enabled: false
    host: localhost
    port: 6379
    stream_key: operation_log
```

## 快速启动

使用如下方式启动:

```bash
python main.py
```

## 使用方法

```python
import asyncio
import uuid
from datetime import datetime

from src.core.logger import AsyncOperationLogger
from src.core.models import OperationLog, LogDetailItem
from src.utils.config import load_config


async def main():
    config = load_config("config/config.yaml")
    operation_logger = AsyncOperationLogger(config)
    await operation_logger.initialize()

    log_detail = LogDetailItem(id=uuid.uuid4().hex, name="vdi", type="admin")
    log_data = OperationLog(
        request_id=uuid.uuid4().hex,
        user_id=uuid.uuid4().hex,
        user_name="vdi",
        obj_id=uuid.uuid4().hex,
        obj_name="Arclient-W",
        ref_id=uuid.uuid4().hex,
        ref_name="abc",
        resource_type="user",
        operation_type="business",
        action="login",
        status="success",
        detail=[log_detail],
        request_ip="127.0.0.1",
        request_params="{}",
        interval_time=0,
        error_code="",
        error_message="",
        extra="{}",
        response_body="{}",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    try:
        await operation_logger.log(log_data)
    finally:
        await operation_logger.close()


if __name__ == "__main__":
    asyncio.run(main())
```