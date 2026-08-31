import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# 数据库位置可由环境变量覆盖（测试时指向独立的 test.db），默认用业务库
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./webhook_1.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

factory = sessionmaker(
    engine,
    expire_on_commit=False,
)

def get_db():
    db = factory()
    try:
        yield db
    finally:
        db.close()

