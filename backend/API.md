# Web Notification System API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In a production environment, you should implement appropriate authentication mechanisms.

## Endpoints

### 1. Register Device

Register a device to receive notifications.

**Endpoint:** `POST /devices/register`

**Request Body:**
```json
{
  "fcm_token": "string"  // Firebase Cloud Messaging token
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/devices/register" \
     -H "Content-Type: application/json" \
     -d '{"fcm_token": "fMEQJGGhSEiM8tK3G8Z..."}'
```

**Success Response:**
```json
{
  "status": "success",
  "message": "Device registered successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid FCM token format
- `500 Internal Server Error`: Server-side error

### 2. Publish Notification

Send a notification to all registered devices.

**Endpoint:** `POST /notifications/publish`

**Request Body:**
```json
{
  "title": "string",       // Required: Notification title
  "body": "string",        // Required: Notification body
  "data": {},             // Optional: Additional data
  "image_url": "string",  // Optional: Image URL
  "action_url": "string"  // Optional: URL to open on click
}
```

**Validation Rules:**
- `title`: 1-100 characters
- `body`: 1-500 characters
- `image_url`: Valid URL format
- `action_url`: Valid URL format

**Example Request:**
```bash
curl -X POST "http://localhost:8000/notifications/publish" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "New Message",
       "body": "You have a new message from John",
       "data": {
         "messageId": "123",
         "sender": "john@example.com"
       },
       "image_url": "https://example.com/image.jpg",
       "action_url": "https://example.com/message/123"
     }'
```

**Success Response:**
```json
{
  "status": "success",
  "message": "Notification queued successfully"
}
```

**Alternative Success Response (Direct FCM):**
```json
{
  "status": "success",
  "message": "Notification sent directly. Success: 1, Failure: 0"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid request body or no registered devices
- `500 Internal Server Error`: Server-side error

## Message Flow

1. When a notification is published:
   - System attempts to queue the message in RabbitMQ
   - If successful, message is processed by consumer
   - If RabbitMQ is unavailable, falls back to direct FCM delivery

2. Consumer processing:
   - Retrieves messages from RabbitMQ queue
   - Sends to FCM in batches
   - Handles failures and retries
   - Acknowledges successful messages

## Testing

You can use the following curl commands for testing:

1. Register a device:
```bash
curl -X POST "http://localhost:8000/devices/register" \
     -H "Content-Type: application/json" \
     -d '{"fcm_token": "YOUR_FCM_TOKEN"}'
```

2. Send a notification:
```bash
curl -X POST "http://localhost:8000/notifications/publish" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Notification",
       "body": "This is a test notification",
       "data": {"test": true}
     }'
```

## Interactive Documentation

FastAPI provides interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The API implements the following error handling:

1. Input Validation:
   - Validates request body format
   - Checks required fields
   - Validates field lengths and formats

2. Runtime Errors:
   - RabbitMQ connection failures
   - FCM sending failures
   - Invalid tokens

3. Server Errors:
   - Returns appropriate HTTP status codes
   - Includes error details in response

## Rate Limiting

Currently, there is no rate limiting implemented. In a production environment, consider adding rate limiting to prevent abuse.

## Monitoring

The API logs important events:
- RabbitMQ connection status
- FCM sending results
- Error conditions

Consider implementing proper monitoring and alerting in production. 