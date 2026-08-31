from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth import verify_api_key
from app.database import get_db
from app import models
from app import schemas
from app.schemas import SubscriptionResponse

router = APIRouter(prefix="/api/subscriptions",
                   tags=["subscriptions"],
                   dependencies=[Depends(verify_api_key)]
)

@router.post("/",response_model=schemas.SubscriptionResponse, status_code=201)
def create_subscription(sub_in: schemas.SubscriptionCreate,
                        db: Session = Depends(get_db)
):
    db_obj = models.Subscription(
        url = sub_in.url,
        secret = sub_in.secret,
        event_types = sub_in.event_types,
        description = sub_in.description
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return db_obj

@router.get("/", response_model=list[SubscriptionResponse], status_code=200)
def found_all_subscriptions(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    db_lst = db.query(models.Subscription).offset(skip).limit(limit).all()
    return db_lst


@router.get("/{id}", response_model=schemas.SubscriptionResponse, status_code=200)
def found_first_subscription(
        id: int,
        db: Session = Depends(get_db)
):
    db_sub = db.get(models.Subscription, id)
    if not db_sub:
        raise HTTPException(status_code=404, detail="not found")
    return db_sub


@router.put("/{id}", response_model=schemas.SubscriptionResponse, status_code=200)
def update_subscription(
        id : int,
        sub_in: schemas.SubscriptionUpdate,
        db: Session = Depends(get_db)
):
    db_sub = db.get(models.Subscription, id)
    if not db_sub:
        raise HTTPException(status_code=404, detail="not found")
    update_data = sub_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_sub, key, value)

    db.commit()
    db.refresh(db_sub)

    return db_sub


@router.delete("/{id}", status_code=204)
def delete_subscription(
        id: int,
        db: Session = Depends(get_db)
):
    db_sub = db.get(models.Subscription, id)
    if not db_sub:
        raise HTTPException(status_code=404, detail="not found")
    db.delete(db_sub)
    db.commit()




