# API Documentation

This document describes the available API endpoints.

## Base URL

```
https://api.project.com/v1
```

## Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### GET /api/info

Get project information.

**Response:**
```json
{
  "name": "project",
  "description": "Project workspace",
  "deployment": {
    "github": true,
    "docker": true
  }
}
```

## Authentication

Currently, no authentication required for public endpoints.

## Rate Limiting

No rate limiting is applied at this time.

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

## SDK Usage

```javascript
const response = await fetch('https://api.project.com/v1/info');
const data = await response.json();
console.log(data);
```

## cURL Examples

```bash
# Get health status
curl -X GET https://api.project.com/v1/health

# Get project info
curl -X GET https://api.project.com/v1/api/info
```