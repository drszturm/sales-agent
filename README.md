# Sales Agent

A FastAPI bridge that connects Evolution API with MCP (Model Context Protocol) servers.

## Features

- Receive messages from Evolution API via webhooks
- Process messages through MCP server
- Send responses back via Evolution API
- Conversation session management
- Docker containerization
- Code quality tools (Ruff)
- Comprehensive test coverage with pytest
- GitHub Actions CI/CD

## Development

### Prerequisites

- Python 3.11+
- Docker (optional)
- Redis

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for development
```
