from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app import schemas
from app.schemas import SubscriptionResponse, EventResponse

router = APIRouter(prefix="/api/events", tags=["events"])

@router.post("/",response_model=schemas.EventResponse,status_code=202)
def create_event(
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

    return evn_obj

@router.get("/",response_model=list[EventResponse],status_code=200)
def found_events(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)
):
    evn_lst = db.query(models.Event).offset(skip).limit(limit).all()
    return evn_lst

