import os
from dotenv import load_dotenv

load_dotenv()

VITE_URL = os.getenv("VITE_URL")
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
