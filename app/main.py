from fastapi import FastAPI
from app.database import engine
from app.database import Base
from app.routers import subscriptions
from app.routers import events

Base.metadata.create_all(engine)

app = FastAPI(
    title="Webhook Relay",
    description="事件转发服务",
    version="0.1.0"
)

app.include_router(subscriptions.router)
app.include_router(events.router)

@app.get("/")
def root():
    return {"message": "Webhook Relay is running"}
