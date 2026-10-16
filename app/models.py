from app.database import Base
from sqlalchemy import String,Integer,DateTime,func,JSON,ForeignKey,Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

# 用户表
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

# 事件表
class Event(Base):
    __tablename__ = 'events'
    id : Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    event_type : Mapped[str] = mapped_column(String(64),index=True)
    payload : Mapped[dict] = mapped_column(JSON,default=dict)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

# 收件箱表
class Delivery(Base):
    __tablename__ = 'deliveries'
    id : Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    event_id : Mapped[int] = mapped_column(ForeignKey("events.id"),index=True)
    subscription_id : Mapped[int] = mapped_column(ForeignKey("subscriptions.id"),index=True)
    status : Mapped[str] = mapped_column(String(32),default="pending",index=True)
    attempt_count : Mapped[int] = mapped_column(Integer,default = 0)
    response_code : Mapped[int] = mapped_column(Integer,nullable=True)
    error_message : Mapped[str] = mapped_column(String(512),nullable=True)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=None,nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    __table_args__ = (
        Index("ix_deliveries_status_next_attempt", "status", "next_attempt_at"),
    )




