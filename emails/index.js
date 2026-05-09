/**
 * Email Service
 * Send transactional emails with templates
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Email templates
const templates = {
  welcome: {
    subject: 'Welcome to {{appName}}!',
    body: `Hello {{name}},

Welcome to {{appName}}! We're excited to have you on board.

Get started by:
1. Verify your email address
2. Complete your profile
3. Explore features

If you have any questions, reply to this email.

Best regards,
The {{appName}} Team`,
  },

  passwordReset: {
    subject: 'Reset your {{appName}} password',
    body: `Hello {{name}},

We received a request to reset your password.

Click the link below to create a new password:
{{resetLink}}

This link expires in {{expiryHours}} hours.

If you didn't request this, you can safely ignore this email.

Best regards,
The {{appName}} Team`,
  },

  orderConfirmation: {
    subject: 'Order #{{orderId}} confirmed',
    body: `Hello {{name}},

Your order #{{orderId}} has been confirmed!

Order Details:
- Items: {{items}}
- Total: {{total}}
- Shipping to: {{shippingAddress}}

We'll notify you when your order ships.

Track your order: {{trackingUrl}}

Best regards,
The {{appName}} Team`,
  },

  notification: {
    subject: '{{title}}',
    body: `Hello {{name}},

{{message}}

{{actionButton}}

Best regards,
The {{appName}} Team`,
  },

  weeklyDigest: {
    subject: 'Your weekly {{appName}} digest',
    body: `Hello {{name}},

Here's your weekly digest:

📊 Activity:
- Logins: {{logins}}
- Actions: {{actions}}

📈 Stats:
{{stats}}

🔔 Recent notifications:
{{notifications}}

Have a great week!

Best regards,
The {{appName}} Team`,
  },
};

// Email provider interface
class EmailProvider {
  constructor(config) {
    this.config = {
      host: process.env.SMTP_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.SMTP_PORT || '465'),
      secure: true,
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
      from: process.env.EMAIL_FROM || 'noreply@project.com',
      fromName: process.env.EMAIL_FROM_NAME || 'Project',
    };
  }

  async send(options) {
    const { to, subject, body, from, fromName } = options;
    
    if (!to || !subject || !body) {
      throw new Error('Missing required fields: to, subject, body');
    }

    // In production, use nodemailer
    console.log(`[Email] Sending to: ${to}`);
    console.log(`[Email] Subject: ${subject}`);

    return {
      success: true,
      messageId: crypto.randomUUID(),
      to,
      subject,
      timestamp: Date.now(),
    };
  }

  async sendTemplate(templateName, data, options) {
    const template = templates[templateName];
    if (!template) {
      throw new Error(`Template not found: ${templateName}`);
    }

    // Template variables
    let subject = this.interpolate(template.subject, data);
    let body = this.interpolate(template.body, data);

    // Add default data
    data.appName = data.appName || 'Project';
    data.from = options.from || this.config.from;
    data.fromName = options.fromName || this.config.fromName;

    return this.send({
      ...options,
      subject,
      body,
    });
  }

  interpolate(text, data) {
    return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return data[key] !== undefined ? data[key] : match;
    });
  }
}

// Email queue for batch sending
class EmailQueue {
  constructor(provider) {
    this.provider = provider;
    this.queue = [];
    this.processing = false;
  }

  async add(to, subject, body, options = {}) {
    this.queue.push({ to, subject, body, options, timestamp: Date.now() });
    
    if (!this.processing && this.queue.length >= 10) {
      this.process();
    }
  }

  async addTemplate(templateName, data, options = {}) {
    const template = templates[templateName];
    if (!template) {
      throw new Error(`Template not found: ${templateName}`);
    }

    const subject = this.provider.interpolate(template.subject, data);
    const body = this.provider.interpolate(template.body, data);

    return this.add(options.to, subject, body, options);
  }

  async process() {
    if (this.processing || this.queue.length === 0) return;
    
    this.processing = true;
    
    while (this.queue.length > 0) {
      const email = this.queue.shift();
      try {
        await this.provider.send({
          to: email.to,
          subject: email.subject,
          body: email.body,
          ...email.options,
        });
      } catch (err) {
        console.error(`[Email] Failed: ${err.message}`);
      }
    }
    
    this.processing = false;
  }

  get size() {
    return this.queue.length;
  }
}

// Export
module.exports = {
  EmailProvider,
  EmailQueue,
  templates,
};

// CLI for testing
if (require.main === module) {
  const provider = new EmailProvider();
  
  // Send welcome email
  provider.sendTemplate('welcome', {
    name: 'John Doe',
    email: 'john@example.com',
  }, {
    to: 'john@example.com',
  }).then(result => {
    console.log('Sent:', result);
  });
}