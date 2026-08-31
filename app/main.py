from fastapi import FastAPI
from app.database import engine
from app.database import Base
from app.routers import subscriptions
from app.routers import events
from app.routers import deliveries
from contextlib import asynccontextmanager
from app.scheduler import start_scheduler, stop_scheduler

Base.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(
    title="Webhook Relay",
    description="事件转发服务",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(subscriptions.router)
app.include_router(events.router)
app.include_router(deliveries.router)

@app.get("/")
def root():
    return {"message": "Webhook Relay is running"}
