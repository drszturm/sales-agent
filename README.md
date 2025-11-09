# Evolution API - MCP Bridge

A FastAPI bridge that connects Evolution API with MCP (Model Context Protocol) servers.

## Features

- Receive messages from Evolution API via webhooks
- Process messages through MCP server
- Send responses back via Evolution API
- Conversation session management
- Redis caching for common messages
- Docker containerization
- Code quality tools (Ruff, Black, Pylint, MyPy)
- Comprehensive test coverage with pytest
- GitHub Actions CI/CD
- RabbitMQ event handling
- DeepSeek AI integration

## Development

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional)
- Redis
- RabbitMQ

### Installation

#### Local Development
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for development
```
3. Copy `.env.example` to `.env` and configure your environment variables
4. Run the application:
```bash
uvicorn main:app --reload
```

#### Docker Development
1. Clone the repository
2. Copy `.env.example` to `.env` and configure your environment variables
3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

### Configuration

Configure the following environment variables in your `.env` file:

```bash
# Evolution API Configuration
EVOLUTION_API_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=your_api_key

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8001
MCP_API_KEY=your_mcp_api_key

# FastAPI Configuration
HOST=0.0.0.0
PORT=8000

# DeepSeek Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Redis Configuration
REDIS_URL=redis://localhost:6379
CACHE_ENABLED=true
CACHE_TTL=3600

# RabbitMQ Configuration
RABBITMQ_URL=amqp://admin:admin@localhost:5672/default
```

### Running Tests

```bash
# Run tests with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing -v

# Run specific test file
pytest tests/test_main.py -v

# Run tests with specific marker
pytest -m "not slow" -v
```

### Code Quality

```bash
# Format code
black .

# Run linter
ruff check .

# Run type checker
mypy .
```

### API Documentation

Once running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Production Deployment

For production deployment, ensure you:

1. Set secure passwords for Redis and RabbitMQ
2. Configure SSL/TLS for all services
3. Set up proper monitoring and logging
4. Use a production-grade web server (e.g., Nginx)
5. Configure proper resource limits in Docker Compose

## License

This project is licensed under the MIT License - see the LICENSE file for details.