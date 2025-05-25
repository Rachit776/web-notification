import pika
import json
import os
from firebase_admin import credentials, messaging, initialize_app
import firebase_admin
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Constants for RabbitMQ
EXCHANGE_NAME = 'notifications'
QUEUE_NAME = 'notification_queue'
ROUTING_KEY = 'notification_route'

# Get absolute path to credentials file
CRED_PATH = str(Path(__file__).parent.parent / "firebase-credentials.json")

# Initialize Firebase Admin SDK
try:
    if not os.path.exists(CRED_PATH):
        raise FileNotFoundError(f"Firebase credentials file not found at: {CRED_PATH}")
        
    cred = credentials.Certificate(CRED_PATH)
    if not firebase_admin._apps:  # Only initialize if not already initialized
        initialize_app(cred)
except Exception as e:
    print(f"Warning: Firebase initialization failed: {e}")
    raise  # We need Firebase for this consumer to work

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

def send_fcm_notification(notification_data):
    try:
        tokens = notification_data.pop('tokens', [])
        if not tokens:
            print("No tokens to send notification to")
            return

        success_count = 0
        failure_count = 0

        # Send to each token individually
        for token in tokens:
            try:
                # Create a message for this specific token
                message = messaging.Message(
                    token=token,
                    notification=messaging.Notification(
                        title=notification_data['title'],
                        body=notification_data['body'],
                        image=notification_data.get('image_url')
                    ),
                    data=notification_data.get('data', {})
                )
                
                # Send the message
                response = messaging.send(message)
                print(f"Successfully sent message to token {token}: {response}")
                success_count += 1
            except Exception as e:
                print(f"Failed to send to token {token}: {e}")
                failure_count += 1

        print(f"Notification sending complete. Success: {success_count}, Failure: {failure_count}")
                    
    except Exception as e:
        print(f"Error sending FCM message: {e}")
        raise  # Re-raise to trigger message nack

def callback(ch, method, properties, body):
    try:
        notification_data = json.loads(body)
        send_fcm_notification(notification_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer():
    while True:
        try:
            connection = get_rabbitmq_connection()
            if not connection:
                print("Failed to connect to CloudAMQP. Retrying in 5 seconds...")
                import time
                time.sleep(5)
                continue

            channel = connection.channel()
            channel = setup_rabbitmq_channel(channel)

            # Set prefetch count
            channel.basic_qos(prefetch_count=1)
            
            # Set up consumer
            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=callback
            )

            print("Starting consumer. Waiting for messages...")
            channel.start_consuming()
            
        except Exception as e:
            print(f"Consumer error: {e}")
            print("Restarting consumer in 5 seconds...")
            import time
            time.sleep(5)

if __name__ == "__main__":
    try:
        start_consumer()
    except KeyboardInterrupt:
        print("Stopping consumer...")
