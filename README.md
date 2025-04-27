# OSS BOSS: AI-Powered Open Source Insights & Automation

![OSS BOSS Logo](/oss-boss.png)

## 🚀 Overview

OSS BOSS is a powerful AI-powered agent designed to help developers, maintainers, and managers analyze and interact with GitHub repositories and NPM packages. Whether you need to check contributor activity, analyze issues, track dependencies, or get insights about popular packages, OSS BOSS has you covered.

## ✨ Features

### GitHub Repository Analysis

- 📊 Get detailed repository information (stars, forks, contributors)
- 👥 Analyze contributor activities and contributions
- 🐞 Track and manage issues
- 🔄 Monitor and examine pull requests
- 🔍 Search code within repositories
- 📝 Add comments to issues and PRs
- 🏷️ Add labels to issues

### NPM Package Analysis

- 📦 Retrieve package metadata and version history
- 📈 Get download statistics
- 🔄 Find package dependents
- ⭐ Check package quality scores
- 🔍 Search for packages by keyword

## 🛠️ Installation

### Prerequisites

- GitHub API Token
- Telegram Bot Token (optional)

### Option 1: Using Docker (Recommended)

The easiest way to get started is using Docker and Docker Compose:

1. Clone the repository:

```bash
git clone https://github.com/hathbanger/oss-boss.git
cd oss-boss
```

2. Create a `.env` file with your credentials:

```bash
# Create and edit .env file
cat > .env << EOF
GITHUB_TOKEN=your_github_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
EOF
```

3. Start the services:

```bash
docker-compose up -d
```

This will:

- Start a MongoDB container
- Build and start the OSS BOSS container
- Connect them via a Docker network
- Make the API available on port 8000

To stop the services:

```bash
docker-compose down
```

### Option 2: Manual Installation

If you prefer to run without Docker:

1. Prerequisites:

   - Python 3.8+
   - MongoDB (for storage and memory)

2. Clone the repository:

```bash
git clone https://github.com/hathbanger/oss-boss.git
cd oss-boss
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
# Create and edit .env file
cp .env.example .env
```

Required environment variables:

```
GITHUB_TOKEN=your_github_token
MONGO_DB_URL=mongodb://localhost:27017/ossboss
```

Optional environment variables:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
API_HOST=0.0.0.0
API_PORT=8000
```

## 🚀 Usage

OSS BOSS provides multiple interfaces to interact with:

### Command Line Interface

```bash
# If using Docker
docker-compose exec ossboss python main.py --cli

# If installed manually
python main.py --cli
```

Example usage:

```
Ask a question (include <owner>/<repo> if needed): facebook/react: What are the top 5 contributors?
```

### API Server

```bash
# If using Docker, the API is started automatically on port 8000

# If installed manually
python main.py --api
```

Then send POST requests to `/analyze` endpoint:

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top 5 contributors?", "repository": "facebook/react"}'
```

### Telegram Bot

```bash
# If using Docker (already set up if TELEGRAM_BOT_TOKEN was provided)
docker-compose exec ossboss python main.py --telegram

# If installed manually
python main.py --telegram
```

Then start a chat with your bot on Telegram and ask questions about repositories:

```
/start
facebook/react: Summarize recent issues
```

### Run All Interfaces

```bash
# If using Docker (default behavior)
docker-compose up

# If installed manually
python main.py --all
```

## 🧠 Example Queries

- "Tell me about tensorflow/tensorflow"
- "babel/babel: Who are the top contributors?"
- "lodash/lodash: Summarize open issues"
- "List recent pull requests in vercel/next.js"
- "Search for React components in facebook/react"
- "Get download stats for express npm package"
- "Find popular packages related to state management"
- "What's the quality score of the axios package?"

## 🧩 Architecture

OSS BOSS is built on the Agno agent framework and uses several components:

- **Main Module**: Manages communication channels (CLI, API, Telegram)
- **Handler**: Initializes the AI agent and processes user queries
- **GitHub Tools**: Toolkit for interacting with GitHub's API
- **NPM Tools**: Toolkit for analyzing NPM packages
- **Communication Interfaces**: CLI, FastAPI server, and Telegram bot implementations

## 🔌 Integration

You can easily integrate OSS BOSS into your existing systems:

- Use the API to embed repository analysis in your applications
- Set up the Telegram bot for team-wide access
- Extend the agent with additional tools and capabilities

### Docker Deployment Options

For production deployments:

1. **Custom MongoDB configuration**:

   - Edit the MongoDB connection settings in docker-compose.yml
   - Or use an external MongoDB instance by setting the `MONGO_DB_URL` environment variable

2. **Custom port mappings**:

   - Modify the ports section in docker-compose.yml to map the API to a different port

3. **Selective interface deployment**:
   - Uncomment the appropriate command in docker-compose.yml to run only specific interfaces
   - For example, use `command: ["python", "main.py", "--api"]` to run only the API server

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Agno](https://github.com/khoj-ai/agno) - The agent framework powering OSS BOSS
- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API client for Python
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram bot interface

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
