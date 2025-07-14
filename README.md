# 🧠 Synapse - AI-Powered Development Assistant

<div align="center">

![Synapse Logo](./templates/a.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com)
[![Contributors Welcome](https://img.shields.io/badge/contributors-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Now-brightgreen)](https://synapse-av8e.onrender.com/)

*Revolutionizing no-code development with AI-powered project planning and code generation*

**🌐 [Visit Live Demo](https://synapse-av8e.onrender.com/)**

[🌟 Features](#features) • [🚀 Quick Start](#quick-start) • [📖 Documentation](#documentation) • [🤝 Contributing](#contributing) • [📄 License](#license)

</div>

## 📝 About

**Synapse** is an ambitious AI-powered development assistant created by **Sumit Kumar Das**, designed to bridge the gap between ideas and implementation. This innovative platform helps developers and non-developers alike by:

- 🎯 Breaking down complex project requirements into actionable tasks
- 🔧 Generating complete codebases based on requirements
- 🐙 Seamlessly integrating with GitHub for version control
- 📊 Providing intelligent project analysis and tech stack recommendations

## ✨ Features

### 🤖 AI-Powered Planning
- **Smart Requirement Analysis**: Convert natural language requirements into structured development tasks
- **Technology Stack Detection**: Automatically identifies the best tech stack for your project
- **Realistic Goal Setting**: Creates achievable milestones and development phases

### 💻 Code Generation
- **Multi-Language Support**: Generates code in various programming languages
- **Complete Project Structure**: Creates entire project scaffolds with proper file organization
- **Best Practices**: Follows industry standards and coding conventions

### 🔗 GitHub Integration
- **Automatic Repository Creation**: Creates and initializes GitHub repositories
- **Code Pushing**: Directly pushes generated code to your GitHub account
- **Issue Management**: Tracks development progress through GitHub issues

### 🎨 Modern UI/UX
- **Space-Themed Interface**: Beautiful, responsive design with animations
- **Dark Mode**: Eye-friendly interface for long coding sessions
- **Real-time Updates**: Live progress tracking and status updates

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js (for frontend dependencies)
- MongoDB (local or cloud instance)
- Google Gemini API key
- GitHub Personal Access Token (optional, for GitHub features)

### 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/skdas20/Synapse.git
   cd Synapse
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r ../requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   MONGODB_URI=mongodb://localhost:27017/synapse
   GITHUB_TOKEN=your_github_token_here  # Optional
   ```

4. **Start the backend server**
   ```bash
   cd backend
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

### 🌐 Local Development

For development with live reload:

```bash
# Terminal 1 - Backend
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Access at http://localhost:8000
```

### 🔑 API Keys Setup

#### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

#### GitHub Token (Optional)
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` permissions
3. Add it to your `.env` file as `GITHUB_TOKEN`

## 📖 API Documentation

Once the server is running, access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/process-requirement` | POST | Analyze requirements and generate tasks |
| `/api/generate-code` | POST | Generate complete codebase |
| `/api/push-to-github` | POST | Push code to GitHub repository |
| `/api/update-github-token` | POST | Update GitHub authentication |

## 🏗️ Project Structure

```
Synapse/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── agents/
│   │   ├── task_planner.py    # AI task planning agent
│   │   ├── dev_bot.py         # Code generation agent
│   │   └── github_agent.py    # GitHub integration agent
│   └── templates/
│       └── a.png              # Logo and assets
├── frontend/
│   ├── index.html             # Main HTML file
│   ├── styles.css             # Styling and animations
│   └── script.js              # Frontend JavaScript
├── generated_project/         # Output directory for generated code
├── requirements.txt           # Python dependencies
├── package.json              # Node.js dependencies
├── Procfile                  # Deployment configuration
└── README.md                 # This file
```

## 🧪 Testing

Run the test suite:

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests (if you add them)
npm test
```

## 🚀 Deployment

### Deploy on Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Service**
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

3. **Configure Environment Variables**
   Add your API keys in Render's dashboard:
   - `GEMINI_API_KEY`
   - `MONGODB_URI`
   - `GITHUB_TOKEN`

### Deploy on Other Platforms

- **Heroku**: Use the included `Procfile`
- **Vercel**: Configure for FastAPI deployment
- **Railway**: Direct GitHub integration

## 🤝 Contributing

We welcome contributions from developers of all skill levels! Here's how you can help:

### 🎯 Areas for Contribution

- **🐛 Bug Fixes**: Help identify and fix issues
- **✨ New Features**: Add innovative functionalities
- **📱 UI/UX Improvements**: Enhance user experience
- **📚 Documentation**: Improve guides and examples
- **🧪 Testing**: Add comprehensive test coverage
- **🔧 Performance**: Optimize code and reduce loading times

### 🚀 Getting Started

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### 📋 Current Issues & Roadmap

Check our [Issues](https://github.com/skdas20/Synapse/issues) for:
- 🟢 **Good First Issues**: Perfect for beginners
- 🟡 **Medium Priority**: For intermediate contributors
- 🔴 **High Priority**: Advanced features and critical fixes

## 🌟 Roadmap

- [ ] **Enhanced Code Editor**: In-browser code editing interface
- [ ] **Multiple AI Models**: Support for different AI providers
- [ ] **Real-time Collaboration**: Multi-user project development
- [ ] **Mobile App**: Native mobile application
- [ ] **Plugin System**: Extensible architecture for custom tools
- [ ] **Advanced Analytics**: Project metrics and insights

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful language model capabilities
- **FastAPI** for the excellent Python web framework
- **MongoDB** for flexible data storage
- **GitHub API** for seamless integration
- **Open Source Community** for inspiration and support

## 📧 Contact

**Sumit Kumar Das** - Creator and Maintainer

- GitHub: [@skdas20](https://github.com/skdas20)
- Project Link: [https://github.com/skdas20/Synapse](https://github.com/skdas20/Synapse)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by [Sumit Kumar Das](https://github.com/skdas20)

</div>

</div>
