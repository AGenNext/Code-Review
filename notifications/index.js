/**
 * Notification System
 * Supports email, webhook, push, and SMS notifications
 */

const https = require('https');
const http = require('http');
const crypto = require('crypto');
const fs = require('fs');

// Notification types
const NotificationType = {
  EMAIL: 'email',
  WEBHOOK: 'webhook',
  PUSH: 'push',
  SMS: 'sms',
  IN_APP: 'in_app',
};

// Notification priority
const Priority = {
  LOW: 'low',
  NORMAL: 'normal',
  HIGH: 'high',
  URGENT: 'urgent',
};

// Base notification class
class Notification {
  constructor(type, options = {}) {
    this.id = crypto.randomUUID();
    this.type = type;
    this.priority = options.priority || Priority.NORMAL;
    this.timestamp = Date.now();
    this.read = false;
  }
}

// Email notification provider
class EmailProvider {
  constructor(config) {
    this.smtp = {
      host: process.env.SMTP_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.SMTP_PORT || '465'),
      secure: true,
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    };
    this.from = process.env.EMAIL_FROM || 'noreply@project.com';
  }

  async send(notification) {
    const { to, subject, body, html } = notification;
    
    // In production, use nodemailer
    console.log(`[Email] Sending to: ${to}, Subject: ${subject}`);
    
    return {
      success: true,
      messageId: crypto.randomUUID(),
      provider: 'email',
    };
  }
}

// Webhook notification provider
class WebhookProvider {
  constructor(config) {
    this.url = process.env.WEBHOOK_URL;
    this.secret = process.env.WEBHOOK_SECRET;
    this.timeout = parseInt(process.env.WEBHOOK_TIMEOUT || '5000');
  }

  async send(notification) {
    if (!this.url) {
      console.warn('[Webhook] No webhook URL configured');
      return { success: false, error: 'No webhook URL' };
    }

    const payload = {
      id: notification.id,
      type: notification.type,
      priority: notification.priority,
      title: notification.title,
      message: notification.message,
      data: notification.data,
      timestamp: notification.timestamp,
    };

    // Sign payload
    if (this.secret) {
      const signature = crypto
        .createHmac('sha256', this.secret)
        .update(JSON.stringify(payload))
        .digest('hex');
      payload.signature = signature;
    }

    const options = {
      hostname: new URL(this.url).hostname,
      path: new URL(this.url).pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Webhook-Signature': payload.signature || '',
      },
      timeout: this.timeout,
    };

    return new Promise((resolve) => {
      const req = https.request(options, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          resolve({
            success: res.statusCode >= 200 && res.statusCode < 300,
            statusCode: res.statusCode,
            provider: 'webhook',
          });
        });
      });

      req.on('error', (err) => {
        resolve({ success: false, error: err.message, provider: 'webhook' });
      });

      req.on('timeout', () => {
        req.destroy();
        resolve({ success: false, error: 'Timeout', provider: 'webhook' });
      });

      req.write(JSON.stringify(payload));
      req.end();
    });
  }
}

// Push notification provider (FCM)
class PushProvider {
  constructor(config) {
    this.serverKey = process.env.FCM_SERVER_KEY;
    this.apiUrl = 'https://fcm.googleapis.com/fcm/send';
  }

  async send(notification) {
    if (!this.serverKey) {
      console.warn('[Push] No FCM server key configured');
      return { success: false, error: 'No FCM server key' };
    }

    const payload = {
      to: notification.token, // FCM device token
      notification: {
        title: notification.title,
        body: notification.message,
        icon: notification.icon,
        click_action: notification.clickAction,
      },
      data: notification.data,
      priority: notification.priority === Priority.HIGH ? 'high' : 'normal',
    };

    const options = {
      hostname: 'fcm.googleapis.com',
      path: '/fcm/send',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `key=${this.serverKey}`,
      },
    };

    return new Promise((resolve) => {
      const req = https.request(options, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          const result = JSON.parse(body);
          resolve({
            success: result.success,
            provider: 'push',
          });
        });
      });

      req.on('error', (err) => {
        resolve({ success: false, error: err.message, provider: 'push' });
      });

      req.write(JSON.stringify(payload));
      req.end();
    });
  }
}

// In-app notification storage
class InAppProvider {
  constructor() {
    this.notifications = new Map();
  }

  async send(notification) {
    const key = notification.userId;
    if (!this.notifications.has(key)) {
      this.notifications.set(key, []);
    }
    
    this.notifications.get(key).push({
      id: notification.id,
      title: notification.title,
      message: notification.message,
      type: notification.type,
      priority: notification.priority,
      timestamp: notification.timestamp,
      read: false,
    });

    return { success: true, provider: 'in_app' };
  }

  async getForUser(userId, { limit = 50, unreadOnly = false } = {}) {
    const notifications = this.notifications.get(userId) || [];
    let result = notifications.sort((a, b) => b.timestamp - a.timestamp);
    
    if (unreadOnly) {
      result = result.filter(n => !n.read);
    }
    
    return result.slice(0, limit);
  }

  async markAsRead(userId, notificationId) {
    const notifications = this.notifications.get(userId) || [];
    const notification = notifications.find(n => n.id === notificationId);
    if (notification) {
      notification.read = true;
      return { success: true };
    }
    return { success: false, error: 'Not found' };
  }

  async clearAll(userId) {
    this.notifications.delete(userId);
    return { success: true };
  }
}

// Notification manager
class NotificationManager {
  constructor() {
    this.providers = {
      [NotificationType.EMAIL]: new EmailProvider(),
      [NotificationType.WEBHOOK]: new WebhookProvider(),
      [NotificationType.PUSH]: new PushProvider(),
      [NotificationType.IN_APP]: new InAppProvider(),
    };
    this.queue = [];
    this.processing = false;
  }

  async send(type, options) {
    const notification = new Notification(type, options);
    Object.assign(notification, options);

    const provider = this.providers[type];
    if (!provider) {
      throw new Error(`Unknown notification type: ${type}`);
    }

    return await provider.send(notification);
  }

  // Broadcast to multiple channels
  async broadcast(channels, options) {
    const results = await Promise.allSettled(
      channels.map(channel => this.send(channel, options))
    );

    return results.map((r, i) => ({
      channel: channels[i],
      ...(r.status === 'fulfilled' ? r.value : { success: false, error: r.reason }),
    }));
  }

  // Queue notification for processing
  async queueNotification(type, options) {
    this.queue.push({ type, options, timestamp: Date.now() });
    
    if (!this.processing) {
      this.processQueue();
    }
  }

  async processQueue() {
    this.processing = true;
    
    while (this.queue.length > 0) {
      const { type, options } = this.queue.shift();
      try {
        await this.send(type, options);
      } catch (err) {
        console.error(`[Notification] Failed to send: ${err.message}`);
      }
    }
    
    this.processing = false;
  }

  // Get in-app notifications
  getInAppNotifications(userId, options) {
    return this.providers[NotificationType.IN_APP].getForUser(userId, options);
  }

  markInAppAsRead(userId, notificationId) {
    return this.providers[NotificationType.IN_APP].markAsRead(userId, notificationId);
  }
}

// Export
module.exports = {
  NotificationManager,
  NotificationType,
  Priority,
  EmailProvider,
  WebhookProvider,
  PushProvider,
  InAppProvider,
};

// Example usage
if (require.main === module) {
  const manager = new NotificationManager();
  
  // Send webhook notification
  manager.send(NotificationType.WEBHOOK, {
    title: 'New User Signup',
    message: 'A new user has signed up',
    data: { userId: '123' },
  }).then(console.log);
  
  // Send in-app notification
  manager.send(NotificationType.IN_APP, {
    userId: 'user123',
    title: 'Welcome!',
    message: 'Thanks for joining us',
  }).then(console.log);
}