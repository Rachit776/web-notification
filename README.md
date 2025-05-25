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

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```env
FIREBASE_CRED_PATH=firebase-credentials.json
CLOUDAMQP_URL=your_cloudamqp_url
FRONTEND_URL=localhost:3000
```

4. Place Firebase credentials in `firebase-credentials.json`

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
VITE_BACKEND_API_URL=http://localhost:8000
VITE_FIREBASE_VAPID_KEY=
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

## 🐳 Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Configuration
Before running with Docker, ensure you have the following files properly configured:

1. Backend configuration:
   - `backend/.env` file with your environment variables
   - `backend/firebase-credentials.json` with your Firebase credentials

2. Frontend configuration:
   - `frontend/.env` file with your environment variables

### Running with Docker

1. Build and start all services:
```bash
docker-compose up --build
```

2. To run in detached mode (background):
```bash
docker-compose up --build -d
```

### Docker Services
The docker-compose configuration includes three services:
- `backend`: FastAPI application (http://localhost:8000)
- `consumer`: RabbitMQ message consumer
- `frontend`: Vite development server (http://localhost:5173)

### Useful Docker Commands

1. View service logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs consumer
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

2. Stop all services:
```bash
docker-compose down
```

3. Restart a specific service:
```bash
docker-compose restart backend
docker-compose restart consumer
docker-compose restart frontend
```

4. Check service status:
```bash
docker-compose ps
```

### Troubleshooting Docker Deployment

1. If services fail to start:
   - Check the logs using `docker-compose logs`
   - Ensure all required environment variables are set
   - Verify that `firebase-credentials.json` is present in the backend directory

2. If frontend can't connect to backend:
   - Check if backend service is running (`docker-compose ps`)
   - Verify the API URL in frontend environment variables
   - Check backend logs for any errors

3. If consumer service fails:
   - Verify RabbitMQ connection string in backend `.env`
   - Check consumer logs for detailed error messages
   - Ensure Firebase credentials are properly configured

## �� API Endpoints

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
