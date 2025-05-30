import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
