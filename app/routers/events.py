from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app import schemas
from app.schemas import EventResponse
from app.services.delivery import deliver_event
from app.auth import verify_api_key


router = APIRouter(prefix="/api/events",
                   tags=["events"],
                   dependencies=[Depends(verify_api_key)]
)

@router.post("/",response_model=schemas.EventResponse,status_code=202)
def create_event(
        background_task: BackgroundTasks,
        evn_in: schemas.EventCreate,
        db: Session = Depends(get_db)
):
    evn_obj = models.Event(
        event_type = evn_in.event_type,
        payload = evn_in.payload
    )
    db.add(evn_obj)
    db.commit()
    db.refresh(evn_obj)
    background_task.add_task(deliver_event, evn_obj.id)

    return evn_obj

@router.get("/",response_model=list[EventResponse],status_code=200)
def found_events(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)
):
    evn_lst = db.query(models.Event).offset(skip).limit(limit).all()
    return evn_lst


@router.get("/{event_id}", response_model=schemas.EventDetailResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    # 1. 查事件，不存在直接 404
    event = db.get(models.Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    deliveries = (
        db.query(models.Delivery)
        .filter(models.Delivery.event_id == event_id)
        .order_by(models.Delivery.id.desc())
        .all()
    )

    # 3. 手动组装嵌套结构：事件字段 + deliveries 列表
    #    Pydantic 会按 EventDetailResponse 验证，嵌套的 ORM 对象
    #    依靠 DeliveryResponse 的 from_attributes=True 自动转换
    return {
        "id": event.id,
        "event_type": event.event_type,
        "payload": event.payload,
        "created_at": event.created_at,
        "deliveries": deliveries,
    }

