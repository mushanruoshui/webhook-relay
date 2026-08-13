from app.database import Base
from sqlalchemy import String,Integer,DateTime,func,JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id : Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    url : Mapped[str] = mapped_column(String(512),nullable=False)
    secret : Mapped[str] = mapped_column(String(256),nullable=False)
    event_types : Mapped[list[str]] = mapped_column(JSON,default=list)
    is_active : Mapped[bool] = mapped_column(default=True)
    description : Mapped[str] = mapped_column(String(256),default="")
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())