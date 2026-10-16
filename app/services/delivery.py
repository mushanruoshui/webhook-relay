from app.database import factory
from app.models import Subscription,Event,Delivery
import httpx
from datetime import datetime, timedelta, timezone
import json, hmac, hashlib, time

BACKOFF_BASE_SECONDS = 60

def _backoff_seconds(attempt_count: int) -> int:
    return BACKOFF_BASE_SECONDS * (2 ** (attempt_count - 1))

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
            _attempt_delivery(delivery.id)
    finally:
        db.close()

def _attempt_delivery(delivery_id):
    db = factory()
    try:
        delivery = db.get(Delivery, delivery_id)
        if not delivery:
            return

        if delivery.status == "delivered":
            return

        if delivery.attempt_count >= delivery.max_attempts:
            delivery.status = 'failed'

            db.commit()
            return

        event = db.get(Event, delivery.event_id)
        subscription = db.get(Subscription, delivery.subscription_id)

        payload_json = json.dumps(event.payload)
        timestamp = str(int(time.time()))
        signing_payload = f"{timestamp}.{payload_json}"
        signature = hmac.new(
            subscription.secret.encode(),
            signing_payload.encode(),
            hashlib.sha256
        ).hexdigest()

        try:
            headers = {
                "X-Relay-Signature": f"t={timestamp},v1={signature}",
                "Content-Type": "application/json",
            }

            response = httpx.post(
                subscription.url,
                content=payload_json.encode(),
                headers=headers,
                timeout=10.0,
            )
            delivery.attempt_count += 1

            if response.status_code < 400:
                delivery.status = 'delivered'
                delivery.response_code = response.status_code
                delivery.error_message = None
                delivery.next_attempt_at = None
            else:
                delivery.response_code = response.status_code
                delivery.error_message = response.text[:512]

                if delivery.attempt_count >= delivery.max_attempts:
                    delivery.status = 'failed'
                    delivery.next_attempt_at = None
                else:
                    delivery.status = 'retrying'
                    delay = _backoff_seconds(delivery.attempt_count)
                    delivery.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)

        except Exception as e:
            delivery.attempt_count += 1
            delivery.response_code = None
            delivery.error_message = f"Unexpected error: {str(e)}"[:512]

            if delivery.attempt_count >= delivery.max_attempts:
                delivery.status = 'failed'
                delivery.next_attempt_at = None
            else:
                delivery.status = 'retrying'
                delay = _backoff_seconds(delivery.attempt_count)
                delivery.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)

        db.commit()
    finally:
        db.close()






