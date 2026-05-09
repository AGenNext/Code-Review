# SSO Configuration

This document describes the SSO authentication setup.

## Supported Providers

- **Google** (OAuth 2.0)
- **GitHub** (OAuth 2.0)
- **Microsoft** (Azure AD)
- **OpenID Connect** (generic)

## Configuration

Set the following environment variables:

```bash
# SSO Provider (google, github, microsoft, oidc)
SSO_PROVIDER=github

# OAuth Client ID
SSO_CLIENT_ID=your-client-id

# OAuth Client Secret
SSO_CLIENT_SECRET=your-client-secret

# Callback URL
SSO_REDIRECT_URI=https://yourdomain.com/auth/callback

# Scopes (space-separated)
SSO_SCOPE=openid profile email
```

## Setup

### 1. GitHub OAuth

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - Application name: Your App
   - Homepage URL: https://yourdomain.com
   - Authorization callback URL: https://yourdomain.com/auth/callback
4. Copy Client ID and generate Client Secret

### 2. Google OAuth

1. Go to Google Cloud Console
2. Create credentials → OAuth client ID
3. Set redirect URI
4. Download credentials JSON

### 3. Microsoft Azure AD

1. Go to Azure Portal → App registrations
2. Create new registration
3. Configure redirect URIs
4. Copy Application (client) ID and Directory (tenant) ID

## Endpoints

### Authorization Request

```
GET /auth?provider=github
```

Redirects to provider's authorization page.

### Callback Handler

```
GET /auth/callback?code=xxx&state=xxx
```

Exchanges code for tokens and creates session.

### Logout

```
POST /auth/logout
```

Clears session and redirects to home.

## User Session

After successful authentication, user session is stored in:
- HTTP-only secure cookie
- Server-side encrypted session store

### Session Claims

```json
{
  "sub": "user-id",
  "email": "user@example.com",
  "name": "User Name",
  "picture": "https://...",
  "provider": "github",
  "iat": 1234567890,
  "exp": 1234571490
}
```

## Code Example

```javascript
// Frontend - Login with SSO
async function loginWithSSO(provider) {
  window.location.href = `/auth?provider=${provider}`;
}

// Frontend - Check auth status
async function getUser() {
  const response = await fetch('/auth/me');
  if (response.ok) {
    return await response.json();
  }
  return null;
}

// Backend - Protect routes
function requireAuth(req, res, next) {
  const user = req.session.user;
  if (!user) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
}
```

## Security Considerations

- Always use HTTPS in production
- Validate state parameter to prevent CSRF
- Use secure, http-only cookies
- Implement token rotation
- Set appropriate session expiration
- Log authentication events