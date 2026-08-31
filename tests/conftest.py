"""
pytest 全局夹具（fixture）：

所有测试文件共享这里定义的东西。
关键动作：在 import app 之前，把数据库指向独立的 test.db，
避免测试污染业务库 webhook_1.db。
"""
import os

# —— 必须在 import app 之前设置环境变量 ——
# 1. 测试库独立：test.db（.gitignore 里的 *.db 已覆盖它）
# 2. API key 固定：测试断言要写死这个值
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["API_KEY"] = "test-api-key-for-pytest"

import pytest
from fastapi.testclient import TestClient

from app.database import engine, Base
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    """每个测试函数跑之前：重建所有表，保证测试之间互不干扰。
    autouse=True 意味着不用在测试里声明，自动对每个测试生效。
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    """模拟的 HTTP 客户端：不发真实网络请求，进程内直接调 FastAPI。
    with 语法触发 lifespan（调度器启停），和真实启动一致。
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers():
    """带正确 API key 的请求头，测试里直接声明使用。"""
    return {"X-API-Key": "test-api-key-for-pytest"}
