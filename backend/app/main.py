from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Optional
import firebase_admin
from firebase_admin import credentials, messaging
import pika
import json
import os
from dotenv import load_dotenv
import urllib.parse
from pathlib import Path

# Load environment variables
load_dotenv()

# Constants for RabbitMQ
EXCHANGE_NAME = 'notifications'
QUEUE_NAME = 'notification_queue'
ROUTING_KEY = 'notification_route'

# Get absolute path to credentials file
CRED_PATH = str(Path(__file__).parent.parent / "firebase-credentials.json")

# Get frontend URLs from environment variable
FRONTEND_URLS = os.getenv('FRONTEND_URLS', 'http://localhost:3000').split(',')

app = FastAPI(
    title="Web Notification System API",
    description="""
    A simple web notification system that manages FCM tokens and delivers notifications using Firebase Cloud Messaging (FCM) and RabbitMQ.
    
    ## Features
    * Device registration for notifications
    * Notification publishing with queuing
    * Support for rich notifications with images and action URLs
    
    ## Flow
    1. Devices register their FCM tokens
    2. Notifications are published to the system
    3. Messages are queued in RabbitMQ
    4. Notifications are delivered via FCM
    """,
    version="1.0.0",
    contact={
        "name": "Rachit Kumar",
        "email": "rachitkumar776@gmail.com",
    },
)

@app.get("/")
async def root():
    """
    Root endpoint that provides API information and health check
    """
    return {
        "status": "healthy",
        "service": "Web Notification System API",
        "version": "1.0.0",
        "endpoints": {
            "root": "/",
            "register_device": "/devices/register",
            "publish_notification": "/notifications/publish"
        }
    }

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Admin SDK
try:
    if not os.path.exists(CRED_PATH):
        raise FileNotFoundError(f"Firebase credentials file not found at: {CRED_PATH}")
        
    cred = credentials.Certificate(CRED_PATH)
    if not firebase_admin._apps:  # Only initialize if not already initialized
        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Warning: Firebase initialization failed: {e}")

# CloudAMQP connection
def get_rabbitmq_connection():
    try:
        # Get the CloudAMQP URL from environment variable
        url = os.getenv('CLOUDAMQP_URL')
        if not url:
            raise ValueError("CLOUDAMQP_URL environment variable not set")

        # Parse the AMQP URL
        params = pika.URLParameters(url)
        
        # Set additional connection parameters
        params.socket_timeout = 5
        params.connection_attempts = 3
        params.retry_delay = 2
        
        # Create and return the connection
        return pika.BlockingConnection(params)
    except Exception as e:
        print(f"Warning: CloudAMQP connection failed: {e}")
        return None

def setup_rabbitmq_channel(channel):
    """Setup RabbitMQ exchange and queue with consistent parameters"""
    try:
        # First try passive declarations to check if they exist
        try:
            channel.exchange_declare(exchange=EXCHANGE_NAME, passive=True)
            channel.queue_declare(queue=QUEUE_NAME, passive=True)
        except pika.exceptions.ChannelClosedByBroker:
            # If they don't exist, create them with full parameters
            channel = channel.connection.channel()  # Reopen channel
            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type='direct',
                durable=True,
                auto_delete=False
            )
            channel.queue_declare(
                queue=QUEUE_NAME,
                durable=True,
                arguments={
                    'x-message-ttl': 3600000  # Messages expire after 1 hour
                }
            )
        
        # Bind the queue to the exchange
        channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=QUEUE_NAME,
            routing_key=ROUTING_KEY
        )
        
        return channel
    except Exception as e:
        print(f"Error setting up RabbitMQ channel: {e}")
        raise

# In-memory storage for FCM tokens (replace with database in production)
fcm_tokens = set()

class DeviceRegistration(BaseModel):
    fcm_token: str = Field(
        ...,
        description="The FCM token obtained from the Firebase JS SDK"
    )
    unsubscribe: bool = Field(
        default=False,
        description="Whether to unsubscribe the token"
    )

class Notification(BaseModel):
    title: str = Field(
        ...,
        description="The title of the notification",
        example="New Message",
        min_length=1,
        max_length=100
    )
    body: str = Field(
        ...,
        description="The body text of the notification",
        example="You have a new message from John",
        min_length=1,
        max_length=500
    )
    data: Optional[Dict] = Field(
        default={},
        description="Additional data to be sent with the notification",
        example={"messageId": "123", "sender": "john@example.com"}
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL of an image to show in the notification",
        example="https://example.com/image.jpg"
    )
    action_url: Optional[str] = Field(
        default=None,
        description="URL to open when the notification is clicked",
        example="https://example.com/message/123"
    )

class NotificationResponse(BaseModel):
    status: str = Field(..., example="success")
    message: str = Field(..., example="Notification queued successfully")

@app.post("/devices/register")
async def register_device(device: DeviceRegistration):
    if device.unsubscribe:
        if device.fcm_token in fcm_tokens:
            fcm_tokens.remove(device.fcm_token)
        return {"status": "success", "message": "Device unsubscribed successfully"}
    else:
        fcm_tokens.add(device.fcm_token)
        return {"status": "success", "message": "Device registered successfully"}

@app.post(
    "/notifications/publish",
    response_model=NotificationResponse,
    tags=["Notifications"],
    summary="Publish a notification",
    description="""
    Publish a notification to all registered devices.
    
    The notification will be:
    1. Queued in RabbitMQ
    2. Processed by the consumer
    3. Sent to all registered devices via FCM
    
    If RabbitMQ is unavailable, the notification will be sent directly via FCM.
    """
)
async def publish_notification(notification: Notification):
    """
    Publish a notification to all registered devices.
    
    - **title**: Notification title (required)
    - **body**: Notification body text (required)
    - **data**: Additional data to send (optional)
    - **image_url**: URL of an image to show (optional)
    - **action_url**: URL to open when clicked (optional)
    
    Returns:
    - **status**: Success status
    - **message**: Confirmation message with delivery details
    """
    try:
        # Try to send via CloudAMQP first
        connection = get_rabbitmq_connection()
        
        if connection:
            try:
                channel = connection.channel()
                channel = setup_rabbitmq_channel(channel)
                
                # Publish message
                message = {
                    "title": notification.title,
                    "body": notification.body,
                    "data": notification.data,
                    "image_url": notification.image_url,
                    "action_url": notification.action_url,
                    "tokens": list(fcm_tokens)
                }
                
                channel.basic_publish(
                    exchange=EXCHANGE_NAME,
                    routing_key=ROUTING_KEY,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                        content_type='application/json'
                    )
                )
                
                connection.close()
                return {"status": "success", "message": "Notification queued successfully"}
            except Exception as e:
                print(f"Error publishing to RabbitMQ: {e}")
                raise

    except Exception as e:
        print(f"Error in publish_notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable for Render deployment
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
