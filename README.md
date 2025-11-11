# Sales Agent

A FastAPI bridge that connects Evolution API with MCP (Model Context Protocol) servers and DeepSeek AI integration.

## Features

- Receive messages from Evolution API via webhooks
- Process messages through MCP server and AI agents
- Send responses back via Evolution API
- Conversation session management
- SQLite database integration
- Redis caching for performance
- Docker containerization with multi-stage builds
- Asynchronous message processing
- LangChain & LangGraph AI orchestration
- DeepSeek AI integration

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Git

## Installation

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/drszturm/sales-agent.git
cd sales-agent
```

2. Create a virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the template:
```bash
cp .env.example .env
```

5. Configure your environment variables in `.env`:
```bash
EVOLUTION_API_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=your_api_key
MCP_SERVER_URL=http://localhost:8001
MCP_API_KEY=your_mcp_api_key
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
REDIS_URL=redis://localhost:6379
```

6. Run the application:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

## Docker Deployment

### Quick Start with Docker Compose

1. Build and run all services:
```bash
docker-compose up --build
```

This will start:
- **Sales Agent API** on `http://localhost:8000`
- **Redis** on `localhost:6379`
- **SQLite Database** in `/app/data/sales_agent.db` (persistent volume)

### Build Docker Image

To build the Docker image manually:
```bash
docker build -t sales-agent:latest .
```

### Run Docker Container

```bash
docker run -d \
  --name sales-agent \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e EVOLUTION_API_KEY=your_api_key \
  -e DEEPSEEK_API_KEY=your_deepseek_key \
  sales-agent:latest
```

### Docker Compose Services

The `docker-compose.yml` includes:

- **app**: Main FastAPI application
- **redis**: Redis cache server

Both services are on the same network and include health checks.

### Environment Variables

Create a `.env` file in the project root:

```bash
# Evolution API
EVOLUTION_API_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=your_evolution_api_key

# MCP Server
MCP_SERVER_URL=http://localhost:8001
MCP_API_KEY=your_mcp_api_key

# DeepSeek AI
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Redis
REDIS_URL=redis://localhost:6379
CACHE_ENABLED=true
CACHE_TTL=3600

# Database
DB_HOST=localhost
DB_NAME=/app/data/sales_agent.db
```

## Development

### Running Tests

```bash
pytest -v
```

With coverage:
```bash
pytest --cov=. --cov-report=html --cov-report=term-missing -v
```

### Code Quality

Format with Black:
```bash
black .
```

Lint with Ruff:
```bash
ruff check .
```

### API Documentation

Once running, access the API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
├── main.py                           # FastAPI application entry point
├── config.py                         # Configuration settings
├── models.py                         # Pydantic models
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Multi-stage Docker build
├── docker-compose.yml                # Docker Compose configuration
├── .dockerignore                     # Docker build exclusions
│
├── agent/                            # AI Agent services
│   ├── deepseek_langchain_service.py
│   ├── deepseek_models.py
│   ├── mcp_client.py
│   └── ...
│
├── messaging/                        # Message handling
│   ├── evolution_client.py
│   ├── message_service.py
│   └── ...
│
├── sales/                            # Sales-specific logic
│   ├── customer_management.py
│   ├── customer_model.py
│   ├── customer_schema.py
│   ├── customer_routes.py
│   └── ...
│
├── infrastructure/                   # Infrastructure layer
│   └── database/
│       └── database.py
│
└── tests/                            # Test suite
    ├── conftest.py
    └── ...
```

## Database

The application uses **SQLite** for data storage (located at `/app/data/sales_agent.db`). 

To initialize the database:
```bash
python -c "from infrastructure.database.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## Performance Considerations

- **Caching**: Redis is used for caching frequently accessed data
- **Async Processing**: FastAPI with async/await for non-blocking I/O
- **Multi-stage Docker Build**: Optimized image size
- **Connection Pooling**: SQLAlchemy connection pooling

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (macOS/Linux)
kill -9 <PID>

# Or change port in command
uvicorn main:app --port 8001
```

### Docker Issues

Clear Docker cache and rebuild:
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Database Connection Issues

Ensure database directory exists and has proper permissions:
```bash
mkdir -p data
chmod 755 data
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/drszturm/sales-agent/issues).
