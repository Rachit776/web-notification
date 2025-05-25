from pydantic import BaseModel

class DeviceRegister(BaseModel):
    fcm_token: str

class NotificationPayload(BaseModel):
    title: str
    body: str
    data: dict = {}
    image_url: str = None
