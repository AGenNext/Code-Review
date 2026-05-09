# Email Service

Transactional email service with templates.

## Configuration

```bash
# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Email Settings
EMAIL_FROM=noreply@project.com
EMAIL_FROM_NAME=Project
```

## Usage

```javascript
const { EmailProvider, EmailQueue, templates } = require('./emails');

const provider = new EmailProvider();

// Send with template
await provider.sendTemplate('welcome', {
  name: 'John',
  appName: 'MyApp',
}, {
  to: 'john@example.com',
});

// Send plain email
await provider.send({
  to: 'user@example.com',
  subject: 'Hello',
  body: 'Message content',
});
```

## Available Templates

| Template | Description | Variables |
|----------|------------|-----------|
| `welcome` | New user welcome | name, appName |
| `passwordReset` | Password reset | name, appName, resetLink, expiryHours |
| `orderConfirmation` | Order confirmation | name, appName, orderId, items, total, shippingAddress |
| `notification` | Generic notification | name, appName, title, message, actionButton |
| `weeklyDigest` | Weekly digest | name, appName, logins, actions, stats |

## Using with Notification System

```javascript
const { NotificationManager, NotificationType } = require('./notifications');
const { EmailProvider } = require('./emails');

const emailProvider = new EmailProvider();
const manager = new NotificationManager();

// Override in-app with email
manager.providers[NotificationType.EMAIL] = emailProvider;

// Now broadcasts include email
await manager.broadcast([NotificationType.EMAIL, NotificationType.IN_APP], {
  title: 'Welcome',
  message: 'Thanks for joining!',
});
```

## Sending HTML Emails

```javascript
const fs = require('fs');

// Read HTML template
const html = fs.readFileSync('./emails/templates/layout.html', 'utf8');

// Replace placeholders
const htmlBody = html
  .replace('{{subject}}', 'Welcome!')
  .replace('{{appName}}', 'MyApp')
  .replace('{{{body}}}', '<p>Hello, welcome!</p>')
  .replace('{{year}}', new Date().getFullYear());

await provider.send({
  to: 'user@example.com',
  subject: 'Welcome!',
  body: htmlBody,
  html: true, // Send as HTML
});
```

## Queue for Batch Sending

```javascript
const { EmailQueue } = require('./emails');

const queue = new EmailProvider();

// Queue emails
await queue.addTemplate('welcome', { name: 'User1' }, { to: 'user1@example.com' });
await queue.addTemplate('welcome', { name: 'User2' }, { to: 'user2@example.com' });
await queue.addTemplate('welcome', { name: 'User3' }, { to: 'user3@example.com' });

// Process queue
queue.process();
```

## Best Practices

1. **Use templates** - Consistent branding
2. **Set sender name** - Recognizable sender
3. **Track opens/clicks** - Use tracking pixels
4. **Handle bounces** - Monitor delivery status
5. **Unsubscribe link** - Required for bulk email