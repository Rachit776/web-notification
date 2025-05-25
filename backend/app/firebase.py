import firebase_admin
from firebase_admin import credentials, messaging
from .utils import FIREBASE_CRED_PATH

cred = credentials.Certificate(FIREBASE_CRED_PATH)
firebase_admin.initialize_app(cred)

def send_fcm_notification(token: str, title: str, body: str, data: dict = None, image_url: str = None):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body, image=image_url),
        token=token,
        data=data or {},
    )
    response = messaging.send(message)
    return response
