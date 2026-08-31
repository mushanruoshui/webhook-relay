from apscheduler.schedulers.background import BackgroundScheduler
from app.services.retry import retry_due_deliveries

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(
        retry_due_deliveries,
        trigger="interval",
        seconds=10,
        id="retry_scan",
    )
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
