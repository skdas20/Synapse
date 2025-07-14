# API Documentation

## Overview

The Synapse API provides endpoints for AI-powered project planning, code generation, and GitHub integration.

**Base URL**: `http://localhost:8000` (development) / `https://your-domain.com` (production)

## Authentication

Currently, the API uses GitHub tokens for GitHub-related operations. User authentication is planned for future releases.

## Endpoints

### Health Check

**GET** `/health`

Check the health status of the application and its services.

**Response:**
```json
{
  "status": "healthy",
  "mongodb": true,
  "task_planner": true,
  "dev_bot": true,
  "github": true
}
```

### Process Requirements

**POST** `/api/process-requirement`

Analyze project requirements and generate development tasks.

**Request Body:**
```json
{
  "requirement": "Create a todo app with React and Node.js"
}
```

**Response:**
```json
{
  "success": true,
  "tasks": [
    "Set up React project structure",
    "Create Express.js backend",
    "Design database schema",
    "Implement CRUD operations",
    "Add user authentication",
    "Create responsive UI components",
    "Add task filtering and sorting",
    "Implement real-time updates",
    "Add data validation",
    "Write unit tests"
  ],
  "techStack": {
    "language": "javascript",
    "frontend": "React",
    "backend": "Node.js",
    "database": "MongoDB"
  },
  "estimatedTime": "2-3 weeks",
  "complexity": "medium"
}
```

### Generate Code

**POST** `/api/generate-code`

Generate complete codebase based on tasks and project type.

**Request Body:**
```json
{
  "tasks": [
    "Set up React project structure",
    "Create Express.js backend"
  ],
  "project_type": "web_application"
}
```

**Response:**
```json
{
  "success": true,
  "project_structure": {
    "frontend/": {
      "src/": {
        "components/": {},
        "pages/": {},
        "App.js": "// React App component code...",
        "index.js": "// React entry point..."
      },
      "package.json": "// Package.json content...",
      "README.md": "// Project README..."
    },
    "backend/": {
      "routes/": {},
      "models/": {},
      "server.js": "// Express server code...",
      "package.json": "// Backend package.json..."
    }
  },
  "download_url": "/api/download-project/abc123"
}
```

### Push to GitHub

**POST** `/api/push-to-github`

Create a GitHub repository and push generated code.

**Request Body:**
```json
{
  "repoName": "my-todo-app",
  "tasks": [
    "Set up React project structure",
    "Create Express.js backend"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "repository_url": "https://github.com/username/my-todo-app",
  "message": "Repository created and code pushed successfully"
}
```

### Update GitHub Token

**POST** `/api/update-github-token`

Update or validate GitHub access token.

**Request Body:**
```json
{
  "token": "ghp_xxxxxxxxxxxxxxxxxxxx"
}
```

**Response:**
```json
{
  "success": true,
  "message": "GitHub token updated successfully",
  "username": "github_username"
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "success": false,
  "error": "Error message description",
  "details": "Additional error details (optional)"
}
```

### Common Error Codes

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Invalid or missing GitHub token
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: External service (AI/GitHub) unavailable

## Rate Limiting

- **Default**: 100 requests per hour per IP
- **Authenticated**: 1000 requests per hour per user (planned)

## Examples

### Using cURL

```bash
# Process requirements
curl -X POST "http://localhost:8000/api/process-requirement" \
  -H "Content-Type: application/json" \
  -d '{"requirement": "Create a todo app with React"}'

# Generate code
curl -X POST "http://localhost:8000/api/generate-code" \
  -H "Content-Type: application/json" \
  -d '{"tasks": ["Setup React"], "project_type": "web"}'
```

### Using JavaScript (Fetch)

```javascript
// Process requirements
const response = await fetch('/api/process-requirement', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    requirement: 'Create a todo app with React'
  })
});

const data = await response.json();
console.log(data.tasks);
```

### Using Python (requests)

```python
import requests

# Process requirements
response = requests.post(
    'http://localhost:8000/api/process-requirement',
    json={'requirement': 'Create a todo app with React'}
)

data = response.json()
print(data['tasks'])
```

## WebSocket Support (Planned)

Future versions will include WebSocket support for:
- Real-time progress updates
- Live collaboration
- Instant notifications

## Pagination (Planned)

For endpoints returning large datasets:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Versioning

The API uses URL versioning:
- Current: `/api/` (v1)
- Future: `/api/v2/`

## Security

### Planned Security Features

- JWT authentication
- Request signing
- Input validation and sanitization
- Rate limiting per user
- CORS configuration
- HTTPS enforcement

## SDKs (Planned)

Official SDKs will be available for:
- JavaScript/TypeScript
- Python
- Go
- Java

## Support

For API support:
- GitHub Issues: [Report bugs or request features](https://github.com/skdas20/Synapse/issues)
- Documentation: [Full documentation](https://github.com/skdas20/Synapse/docs)
- Email: Contact the maintainer through GitHub
