/**
 * SSO Authentication Server
 * Supports OAuth2/OpenID Connect with multiple providers
 */

const crypto = require('crypto');
const https = require('https');
const http = require('http');
const url = require('url');
const fs = require('fs');

// Configuration from environment
const config = {
  provider: process.env.SSO_PROVIDER || 'github',
  clientId: process.env.SSO_CLIENT_ID,
  clientSecret: process.env.SSO_CLIENT_SECRET,
  redirectUri: process.env.SSO_REDIRECT_URI || 'http://localhost:8080/auth/callback',
  scope: process.env.SSO_SCOPE || 'openid profile email',
  sessionSecret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString('hex'),
  port: parseInt(process.env.PORT || '8080'),
};

// Provider configurations
const providers = {
  github: {
    authUrl: 'https://github.com/login/oauth/authorize',
    tokenUrl: 'https://github.com/login/oauth/access_token',
    userUrl: 'https://api.github.com/user',
    scope: 'read:user user:email',
  },
  google: {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    userUrl: 'https://www.googleapis.com/oauth2/v2/userinfo',
    scope: 'openid profile email',
  },
  microsoft: {
    authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    tokenUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    userUrl: 'https://graph.microsoft.com/v1.0/me',
    scope: 'openid profile email',
  },
};

// Sessions storage (use Redis in production)
const sessions = new Map();

// Generate state token
function generateState() {
  return crypto.randomBytes(32).toString('hex');
}

// Encrypt session data
function encryptSession(data) {
  const key = crypto.scryptSync(config.sessionSecret, 'salt', 32);
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
  let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

// Decrypt session data
function decryptSession(encryptedData) {
  try {
    const key = crypto.scryptSync(config.sessionSecret, 'salt', 32);
    const [ivHex, encrypted] = encryptedData.split(':');
    const iv = Buffer.from(ivHex, 'hex');
    const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return JSON.parse(decrypted);
  } catch {
    return null;
  }
}

// Build authorization URL
function getAuthorizationUrl(provider) {
  const p = providers[provider];
  const state = generateState();
  const params = new URLSearchParams({
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    scope: p.scope,
    state: state,
    response_type: 'code',
  });
  return { url: p.authUrl + '?' + params, state };
}

// Exchange code for tokens
async function exchangeCodeForTokens(provider, code) {
  const p = providers[provider];
  const data = new URLSearchParams({
    client_id: config.clientId,
    client_secret: config.clientSecret,
    code: code,
    redirect_uri: config.redirectUri,
  });
  
  const options = {
    hostname: url.parse(p.tokenUrl).hostname,
    path: url.parse(p.tokenUrl).path,
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
    },
  };
  
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch {
          reject(new Error('Failed to parse token response'));
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Get user info from provider
async function getUserInfo(provider, accessToken) {
  const p = providers[provider];
  
  const options = {
    hostname: url.parse(p.userUrl).hostname,
    path: p.userUrl.pathname || url.parse(p.userUrl).path,
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Accept': 'application/json',
    },
  };
  
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch {
          reject(new Error('Failed to parse user response'));
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

// Create session cookie
function createSession(user) {
  const sessionId = crypto.randomBytes(32).toString('hex');
  const session = {
    user,
    createdAt: Date.now(),
    expiresAt: Date.now() + 24 * 60 * 60 * 1000, // 24 hours
  };
  sessions.set(sessionId, session);
  return sessionId;
}

// Clear session
function clearSession(sessionId) {
  sessions.delete(sessionId);
}

// Router
const routes = {
  '/auth': async (req, res) => {
    const query = new URL(req.url, 'http://localhost').searchParams;
    const provider = query.get('provider') || config.provider;
    
    // Check if already authenticated
    const cookieHeader = req.headers.cookie || '';
    const sessionMatch = cookieHeader.match(/session=([^;]+)/);
    if (sessionMatch) {
      const user = decryptSession(sessionMatch[1]);
      if (user) {
        res.writeHead(302, { Location: '/' });
        res.end();
        return;
      }
    }
    
    const { url, state } = getAuthorizationUrl(provider);
    res.writeHead(302, {
      'Location': url,
      'Set-Cookie': `state=${state}; Path=/; HttpOnly; SameSite=Lax`,
    });
    res.end();
  },
  
  '/auth/callback': async (req, res) => {
    const query = new URL(req.url, 'http://localhost').searchParams;
    const code = query.get('code');
    const state = query.get('state');
    const error = query.get('error');
    
    // Validate state
    const cookieHeader = req.headers.cookie || '';
    const stateMatch = cookieHeader.match(/state=([^;]+)/);
    if (!stateMatch || stateMatch[1] !== state) {
      res.writeHead(400, { 'Content-Type': 'text/html' });
      res.end('Invalid state parameter');
      return;
    }
    
    if (error) {
      res.writeHead(400, { 'Content-Type': 'text/html' });
      res.end('Authorization failed: ' + error);
      return;
    }
    
    if (!code) {
      res.writeHead(400, { 'Content-Type': 'text/html' });
      res.end('No authorization code provided');
      return;
    }
    
    try {
      // Exchange code for tokens
      const tokens = await exchangeCodeForTokens(config.provider, code);
      
      // Get user info
      const userInfo = await getUserInfo(config.provider, tokens.access_token);
      
      // Normalize user data
      const user = {
        id: userInfo.id,
        name: userInfo.name || userInfo.login || userInfo.displayName,
        email: userInfo.email || userInfo.emails?.[0]?.value,
        picture: userInfo.avatar_url || userInfo.picture,
        provider: config.provider,
      };
      
      // Create session
      const sessionId = createSession(user);
      const encrypted = encryptSession({ ...user, iat: Date.now() });
      
      res.writeHead(302, {
        'Location': '/',
        'Set-Cookie': [
          `session=${encrypted}; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400`,
          'state=; Path=/; Max-Age=0',
        ],
      });
      res.end();
    } catch (err) {
      console.error('Auth error:', err);
      res.writeHead(500, { 'Content-Type': 'text/html' });
      res.end('Authentication failed');
    }
  },
  
  '/auth/logout': async (req, res) => {
    const cookieHeader = req.headers.cookie || '';
    const sessionMatch = cookieHeader.match(/session=([^;]+)/);
    
    if (sessionMatch) {
      clearSession(sessionMatch[1]);
    }
    
    res.writeHead(302, {
      'Location': '/',
      'Set-Cookie': [
        'session=; Path=/; HttpOnly; Max-Age=0',
      ],
    });
    res.end();
  },
  
  '/auth/me': async (req, res) => {
    const cookieHeader = req.headers.cookie || '';
    const sessionMatch = cookieHeader.match(/session=([^;]+)/);
    
    if (!sessionMatch) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Not authenticated' }));
      return;
    }
    
    const user = decryptSession(sessionMatch[1]);
    if (!user) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid session' }));
      return;
    }
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(user));
  },
  
  '/health': async (req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('OK');
  },
};

// Start server
function startServer(port) {
  const server = http.createServer((req, res) => {
    const pathname = new URL(req.url, 'http://localhost').pathname;
    const handler = routes[pathname];
    
    if (handler) {
      handler(req, res);
    } else {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not Found');
    }
  });
  
  server.listen(port, () => {
    console.log(`Auth server running on port ${port}`);
  });
  
  return server;
}

// Export for testing
module.exports = { startServer, routes, config };

// Run if main
if (require.main === module) {
  if (!config.clientId || !config.clientSecret) {
    console.error('Please set SSO_CLIENT_ID and SSO_CLIENT_SECRET environment variables');
    process.exit(1);
  }
  startServer(config.port);
}