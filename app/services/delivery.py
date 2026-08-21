from app.database import factory
from app.models import Subscription,Event,Delivery
import httpx

def deliver_event(event_id: int):
    db = factory()
    try:
        event = db.get(Event, event_id)
        if not event:
            return

        subscriptions = db.query(Subscription).filter(Subscription.is_active == True).all()
        matching = [s for s in subscriptions if event.event_type in s.event_types]

        for sub in matching:
            delivery = Delivery(
                event_id=event.id,
                subscription_id=sub.id,
            )
            db.add(delivery)
            db.commit()
            db.refresh(delivery)

            try:
                response = httpx.post(sub.url, json=event.payload, timeout=10.0)
                if response.status_code < 400:
                    delivery.status = "delivered"
                    delivery.response_code = response.status_code
                else:
                    delivery.status = "failed"
                    delivery.response_code = response.status_code
                    delivery.error_message = f"错误信息:{response.text[:512]}"
                delivery.attempt_count = 1
            except Exception as e:
                delivery.status = 'failed'
                delivery.error_message = str(e)[:512]
                delivery.attempt_count = 1

            db.commit()
    finally:
        db.close()
