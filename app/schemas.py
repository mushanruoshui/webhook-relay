from pydantic import BaseModel,Field
from datetime import datetime

class SubscriptionCreate(BaseModel):
    url: str = Field(
            ...,
        max_length=512,
        description="订阅地址"
        )

    secret: str = Field(
            ...,
        min_length=8,
        max_length=256,
        description="订阅密钥"
        )

    event_types: list[str] = Field(
        default=[],
        description="事件类型列表"
        )

    description: str = Field(
        default="",
        max_length=256,
        description="订阅描述"
        )


class SubscriptionUpdate(BaseModel):
    url: str | None = Field(default=None, max_length=512)
    secret: str | None = Field(
        default=None,
        min_length=8,
        max_length=256,
        description="订阅密钥"
    )
    event_types: list[str] | None = None
    description: str | None = Field(default=None, max_length=256)

class SubscriptionResponse(BaseModel):
    id: int = Field(description = "订阅id")

    url: str = Field(
        ...,
        max_length=512,
        description="订阅地址"
    )

    secret: str = Field(
        ...,
        min_length=8,
        max_length=256,
        description="订阅密钥"
    )

    event_types: list[str] = Field(
        default=list,
        description="事件类型列表"
    )

    description: str = Field(
        default="",
        max_length=256,
        description="订阅描述"
    )

    is_active: bool = Field(default=True)

    created_at: datetime

    updated_at: datetime

    model_config = {"from_attributes":True}

class EventCreate(BaseModel):
    event_type: str = Field(max_length=64)
    payload: dict

class EventResponse(BaseModel):
    id: int
    event_type: str
    payload: dict
    created_at: datetime

    model_config = {"from_attributes": True}

class DeliveryResponse(BaseModel):
    id: int
    event_id: int
    subscription_id: int
    status: str
    attempt_count: int
    response_code: int | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}



