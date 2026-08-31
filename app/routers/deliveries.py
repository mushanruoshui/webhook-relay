from app.auth import verify_api_key
from fastapi import APIRouter, Depends, Query
from app.services.retry import retry_due_deliveries
from app.database import get_db
from sqlalchemy.orm import Session
from app import models
from app import schemas

router = APIRouter(prefix="/api/deliveries",
                   tags=["deliveries"],
                   dependencies=[Depends(verify_api_key)]
)

@router.post("/retry")
def trigger_retry():
    count = retry_due_deliveries()
    return {"retried": count}

@router.get("", response_model=schemas.DeliveryListResponse)
def deliveries(
    status: str = Query(None, description="按状态过滤：pending/delivered/retrying/failed"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(models.Delivery)

    if status:
        query = query.filter(models.Delivery.status == status)

    total = query.count()

    items = (
        query
        .order_by(models.Delivery.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {"total": total, "items": items}

