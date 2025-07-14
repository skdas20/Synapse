# Development Setup Guide

## Prerequisites

Before setting up the development environment, ensure you have the following installed:

### Required Software

1. **Python 3.8 or higher**
   - Download from [python.org](https://python.org)
   - Verify installation: `python --version`

2. **Git**
   - Download from [git-scm.com](https://git-scm.com)
   - Verify installation: `git --version`

3. **Node.js (Optional - for package.json scripts)**
   - Download from [nodejs.org](https://nodejs.org)
   - Verify installation: `node --version`

### Database

Choose one of the following MongoDB options:

#### Option 1: Local MongoDB
1. Download from [mongodb.com](https://mongodb.com/try/download/community)
2. Install and start MongoDB service
3. Default connection: `mongodb://localhost:27017`

#### Option 2: MongoDB Atlas (Cloud)
1. Create account at [mongodb.com](https://mongodb.com)
2. Create a free cluster
3. Get connection string from Atlas dashboard

### API Keys

#### Google Gemini AI API Key (Required)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Create new API key
4. Copy the key for environment configuration

#### GitHub Personal Access Token (Optional)
1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Select scopes: `repo`, `user`
4. Copy the token for environment configuration

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/skdas20/Synapse.git
cd Synapse
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configurations
# Use any text editor (notepad, vim, vscode, etc.)
```

**Required .env Configuration:**
```env
# Required
GEMINI_API_KEY=your_actual_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017/synapse

# Optional (for GitHub features)
GITHUB_TOKEN=your_github_token_here

# Optional (for development)
DEBUG=true
LOG_LEVEL=INFO
```

### 5. Database Setup

#### For Local MongoDB:
```bash
# Start MongoDB service
# On Windows (if installed as service):
net start MongoDB

# On macOS:
brew services start mongodb-community

# On Linux:
sudo systemctl start mongod
```

#### Test Database Connection:
```bash
# Using MongoDB Shell
mongosh "mongodb://localhost:27017/synapse"

# Or using Python
python -c "from pymongo import MongoClient; print('Connected!' if MongoClient('mongodb://localhost:27017').server_info() else 'Failed!')"
```

## Running the Application

### Development Mode

```bash
# Navigate to backend directory
cd backend

# Start the development server with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Alternative: Start with custom settings
uvicorn app:app --reload --host 127.0.0.1 --port 8000 --log-level info
```

### Production Mode

```bash
# Using Gunicorn (production WSGI server)
cd backend
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or using Uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access the Application

1. **Frontend**: Open browser to `http://localhost:8000`
2. **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
3. **Alternative API Docs**: `http://localhost:8000/redoc`
4. **Health Check**: `http://localhost:8000/health`

## Development Workflow

### Code Structure

```
Synapse/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main application
│   ├── agents/             # AI agents
│   │   ├── task_planner.py # Task planning agent
│   │   ├── dev_bot.py      # Code generation agent
│   │   └── github_agent.py # GitHub integration
│   └── templates/          # Static assets
├── frontend/               # Frontend files
│   ├── index.html         # Main HTML
│   ├── styles.css         # Styling
│   └── script.js          # JavaScript
├── docs/                  # Documentation
├── generated_project/     # Generated code output
└── tests/                 # Test files (to be created)
```

### Making Changes

1. **Backend Changes**: Modify files in `backend/` directory
   - FastAPI automatically reloads in development mode
   - Check logs in terminal for errors

2. **Frontend Changes**: Modify `index.html`, `styles.css`, `script.js`
   - Refresh browser to see changes
   - Use browser developer tools for debugging

3. **API Changes**: Update `backend/app.py`
   - Check updated documentation at `/docs`
   - Test endpoints with Swagger UI

### Testing Your Changes

```bash
# Test API endpoints
curl http://localhost:8000/health

# Test requirement processing
curl -X POST "http://localhost:8000/api/process-requirement" \
  -H "Content-Type: application/json" \
  -d '{"requirement": "Create a simple website"}'

# Test frontend
# Open browser to http://localhost:8000 and test UI
```

## Debugging

### Common Issues

#### 1. Import Errors
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. MongoDB Connection Issues
```bash
# Check if MongoDB is running
# Windows:
net start MongoDB

# macOS:
brew services start mongodb-community

# Linux:
sudo systemctl status mongod
```

#### 3. Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Kill the process or use different port
uvicorn app:app --port 8001
```

#### 4. API Key Issues
```bash
# Verify environment variables are loaded
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"

# Check .env file exists and has correct values
cat .env  # macOS/Linux
type .env # Windows
```

### Logging

Enable detailed logging for debugging:

```python
# Add to backend/app.py for more verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Browser Developer Tools

1. Open browser developer tools (F12)
2. **Console**: Check for JavaScript errors
3. **Network**: Monitor API requests and responses
4. **Elements**: Inspect HTML and CSS
5. **Application**: Check localStorage and cookies

## IDE Setup

### VS Code (Recommended)

Install recommended extensions:
```bash
# Python extension
code --install-extension ms-python.python

# JavaScript/HTML/CSS support
code --install-extension ms-vscode.vscode-html-languageservice

# FastAPI support
code --install-extension ms-python.flake8
```

**VS Code Settings (.vscode/settings.json):**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### PyCharm

1. Open project in PyCharm
2. Configure Python interpreter to use `venv/bin/python`
3. Mark `backend` as sources root
4. Configure run configuration for `uvicorn app:app --reload`

## Next Steps

1. **Explore the Code**: Start with `backend/app.py` and `index.html`
2. **Read the API Documentation**: Visit `/docs` when server is running
3. **Check Issues**: Look for "good first issue" labels on GitHub
4. **Make Your First Contribution**: Fix a bug or add a feature
5. **Join the Community**: Participate in discussions and code reviews

## Getting Help

- **Documentation**: Check `docs/` folder for detailed guides
- **Issues**: Create GitHub issue for bugs or questions
- **Discussions**: Use GitHub Discussions for community help
- **Code Review**: Submit PR for feedback and learning

Happy coding! 🚀
