from app.database import factory
from app.models import Delivery
from datetime import datetime, timezone
from app.services.delivery import _attempt_delivery

def retry_due_deliveries() -> int:
    db = factory()
    try:
        due = db.query(Delivery).filter(
            Delivery.status == 'retrying',
            Delivery.next_attempt_at <= datetime.now(timezone.utc),
            Delivery.attempt_count < Delivery.max_attempts,
        ).all()

        count = 0
        for delivery in due:
            _attempt_delivery(delivery.id)
            count += 1
        return count
    finally:
        db.close()
