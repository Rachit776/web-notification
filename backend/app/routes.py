from fastapi import APIRouter
from .models import DeviceRegister, NotificationPayload
from .consumer import register_token
import aio_pika
import json
from .utils import RABBITMQ_URL

router = APIRouter()
TOKENS = []

@router.post("/devices/register")
def register_device(payload: DeviceRegister):
    register_token(payload.fcm_token)
    return {"status": "registered"}

@router.post("/notifications/publish")
async def publish_notification(payload: NotificationPayload):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(payload.dict()).encode()),
        routing_key="notifications",
    )
    return {"status": "published"}
