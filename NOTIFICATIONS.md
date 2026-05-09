# Notification System

This document describes the notification system and available channels.

## Overview

The notification system supports multiple delivery channels:
- **Email** - Traditional email notifications
- **Webhooks** - HTTP callbacks to external services
- **Push** - Firebase Cloud Messaging (FCM) for mobile/web push
- **In-App** - Real-time notifications within the application

## Configuration

### Email Notifications

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
EMAIL_FROM=noreply@project.com
```

### Webhook Notifications

```bash
WEBHOOK_URL=https://your-webhook.com/hook
WEBHOOK_SECRET=your-secret-key
WEBHOOK_TIMEOUT=5000
```

### Push Notifications

```bash
FCM_SERVER_KEY=your-fcm-server-key
```

## Usage

### JavaScript/Node.js

```javascript
const { NotificationManager, NotificationType, Priority } = require('./notifications');

const manager = new NotificationManager();

// Send single notification
await manager.send(NotificationType.WEBHOOK, {
  title: 'New Order',
  message: 'You have a new order #12345',
  priority: Priority.HIGH,
  data: { orderId: '12345' },
});

// Send to multiple channels
await manager.broadcast(
  [NotificationType.EMAIL, NotificationType.IN_APP],
  {
    title: 'Welcome',
    message: 'Thanks for signing up!',
    userId: 'user123',
  }
);
```

### In-App Notifications

```javascript
// Get user notifications
const notifications = await manager.getInAppNotifications('user123', {
  limit: 20,
  unreadOnly: true,
});

// Mark as read
await manager.markInAppAsRead('user123', 'notification-id');
```

## API Endpoints

### POST /notifications

Send a notification.

**Request:**
```json
{
  "channel": "webhook",
  "title": "Title",
  "message": "Message",
  "priority": "high"
}
```

**Response:**
```json
{
  "success": true,
  "messageId": "xxx"
}
```

### GET /notifications/:userId

Get in-app notifications for user.

### PATCH /notifications/:userId/:notificationId/read

Mark notification as read.

## Events

The system emits the following events:

- `notification:sent` - After successful delivery
- `notification:failed` - After delivery failure
- `notification:clicked` - When user clicks notification

## Best Practices

1. **Use appropriate priority levels** - High priority for urgent notifications
2. **Batch notifications** - Queue during high load periods
3. **Handle failures gracefully** - Implement retry logic
4. **Respect user preferences** - Allow opting out of channels