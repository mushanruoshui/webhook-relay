from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///./webhook.db", connect_args={"check_same_thread": False})

async_factory = sessionmaker(
    engine,
    expire_on_commit=False,
)

def get_db():
    db = async_factory()
    try:
        yield db
    finally:
        db.close()

