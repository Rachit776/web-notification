# Web Notification System

A real-time web notification system built with FastAPI, RabbitMQ, and Firebase Cloud Messaging (FCM). This system enables web applications to send and receive push notifications efficiently using a message queue architecture.

## 🚀 Features

- Real-time push notifications using Firebase Cloud Messaging
- Message queuing with RabbitMQ (CloudAMQP)
- FastAPI backend with async support
- Vanilla JavaScript frontend
- Service Worker for background notifications
- Subscribe/Unsubscribe functionality
- Fallback to direct FCM if queue is unavailable

## 🏗️ Architecture

### Frontend
- Vanilla JavaScript with Vite
- Firebase Cloud Messaging client
- Service Worker for background notifications
- Local storage for subscription state

### Backend
- FastAPI for REST API endpoints
- RabbitMQ for message queuing
- Firebase Admin SDK for sending notifications
- In-memory token storage (can be extended to database)

## 🛠️ Prerequisites

- Python 3.8+
- Node.js 14+
- Firebase project with Cloud Messaging enabled
- CloudAMQP account

## ⚙️ Configuration

### Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Enable Cloud Messaging
3. Generate Firebase Admin SDK credentials
4. Get your Firebase client configuration

### CloudAMQP Setup

1. Create an account at [CloudAMQP](https://www.cloudamqp.com)
2. Create a new instance
3. Get the AMQP URL

## 📦 Installation

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
FIREBASE_CRED_PATH=firebase-credentials.json
CLOUDAMQP_URL=your_cloudamqp_url
```

5. Place Firebase credentials in `firebase-credentials.json`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```env
VITE_FIREBASE_CONFIG=your_firebase_config
```

## 🚀 Running the Application

### Start Backend

1. Start the FastAPI server:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. Start the consumer in a separate terminal:
```bash
cd backend
python app/consumer.py
```

### Start Frontend

1. Run the development server:
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📡 API Endpoints

### Register Device

Register a device for notifications.

```http
POST /devices/register
Content-Type: application/json

{
  "fcm_token": "string",
  "unsubscribe": false
}
```

### Publish Notification

Send a notification to all registered devices.

```http
POST /notifications/publish
Content-Type: application/json

{
  "title": "string",
  "body": "string",
  "data": {},
  "image_url": "string",
  "action_url": "string"
}
```

## 🔄 Message Flow

1. Client subscribes to notifications:
   - Requests notification permission
   - Gets FCM token
   - Registers token with backend

2. When publishing a notification:
   - Message is sent to RabbitMQ queue
   - Consumer processes the message
   - Notification is sent via FCM
   - Clients receive the notification

3. Fallback mechanism:
   - If RabbitMQ is unavailable
   - Direct FCM delivery is used

## 🔒 Security Considerations

- Firebase credentials are kept secure
- CORS is properly configured
- Environment variables for sensitive data
- Service worker scope is limited
- Token validation on backend

## 🚧 Error Handling

- Queue connection failures
- FCM sending failures
- Permission denials
- Token registration errors
- Network issues

## 🔍 Monitoring

The system logs important events:
- Queue connection status
- Message processing status
- FCM delivery results
- Error conditions

## 🛠️ Development

### Code Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── consumer.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   └── firebase.js
│   ├── public/
│   │   └── firebase-messaging-sw.js
│   └── package.json
└── README.md
```

### Adding Features

1. Backend:
   - Add new endpoints in `main.py`
   - Extend consumer in `consumer.py`
   - Update requirements if needed

2. Frontend:
   - Modify notification handling in `main.js`
   - Update service worker as needed
   - Add new UI components

## 📝 License

MIT License

## 👤 Author

Rachit Kumar
- Email: rachitkumar776@gmail.com