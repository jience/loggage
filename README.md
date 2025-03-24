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
    English | <a href="README_zh.md">中文</a>
  </p>
</div>

# Introduction

`Loggage` is a universal component designed to record operation logs. It enables you to log operational records of your business systems by leveraging decorators or simply invoking regular functions, while maintaining minimal impact on your business code. Additionally, it provides flexibility in storing operation logs, allowing you to choose different storage solutions based on your project needs. Loggage supports a variety of storage options, including relational databases like MySQL, search engines like Elasticsearch, and in-memory data stores like Redis.
## 主要特性

- **Fully asynchronous**: Supports the async/await asynchronous system architecture safely
- **Exception safety**: Logging operations will not disrupt the API's normal execution
- **Type safety**: Data validation based on Pydantic models
- **High performance**: Logging operations are fully asynchronous
- **Easy to extend**: Factory pattern + standard interface facilitates adding new storage processors (recommended phrasing: plug-in architecture)
- **Configuration-driven**: Uses YAML-based configuration files for flexible control of storage mechanisms

## Installation

1. Install uv (A fast Python package installer and resolver):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:

```bash
git clone https://github.com/jience/loggage.git
cd loggage
```

3. Create a new virtual environment and activate it:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# Or on Windows:
# .venv\Scripts\activate
```

4. Install dependencies:

```bash
uv pip install -r requirements.txt
```

## Configuration

Follow these steps to set up your configuration:

1. Create a `config.yaml` file in the `config` directory (you can copy from the example):

```bash
cp config/config.example.yaml config/config.yaml
```

2. Edit `config/config.yaml` to customize settings:

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

## Quick Start

One line for run:

```bash
python main.py
```

## Usage

```python
import asyncio
from datetime import datetime

from src.core.logger import AsyncOperationLogger
from src.core.models import OperationLog, LogDetailItem
from src.utils.config import load_config
from src.utils.tools import generate_uuid_str


async def main():
    config = load_config("config/config.yaml")

    async with AsyncOperationLogger(config) as op_logger:
        log_detail = LogDetailItem(id=generate_uuid_str(), name="vdi", type="admin")
        log_data = OperationLog(
            request_id=generate_uuid_str(),
            user_id=generate_uuid_str(),
            user_name="vdi",
            obj_id=generate_uuid_str(),
            obj_name="Client-W",
            ref_id=generate_uuid_str(),
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
        await op_logger.log(log_data)
        # 或批量处理
        # await op_logger.log_batch([log_data, log_data, log_data])


if __name__ == "__main__":
    asyncio.run(main())
```