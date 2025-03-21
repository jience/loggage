<a name="readme-top"></a>

<div align="center">
  <img src="./loggage.png" align="center" width="441" alt="Project icon">
  <h1 align="center">Loggage: Code Less, Make More</h1>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/uv-32173c?logo=uv&logoColor=fff">
  <img src="https://img.shields.io/badge/Ruff-6340ac?logo=Ruff&logoColor=fff">
  <img src="https://img.shields.io/badge/Python-3.10-34D058">
</div>

# Introduction

Loggage allow you to store operation log in defferent locations, such as MySQL, Redis, Influxdb, Elasticsearch, and more.

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
import uuid
from datetime import datetime

from src.core.logger import OperationLogger
from src.core.models import OperationLog, LogDetailItem
from src.utils.config import load_config


async def main():
    config = load_config("config/config.yaml")
    operation_logger = OperationLogger(config)
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