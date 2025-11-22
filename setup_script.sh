#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update the system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "Installing essential packages: python3-venv, python3-dev, libpq-dev, postgresql, postgresql-contrib, redis-server, nginx, curl, git"
sudo apt install python3-venv python3-dev libpq-dev postgresql postgresql-contrib redis-server nginx curl git -y

# --- PostgreSQL Setup ---
echo "Setting up PostgreSQL..."
# Note: By default, a 'postgres' user is created. You can set a password for this user
# and create a specific database and user for your application manually later
# using `sudo -u postgres psql`.
sudo systemctl enable postgresql
sudo systemctl start postgresql
echo "PostgreSQL installed and running. Default user is 'postgres'."
echo "You can access the PostgreSQL shell using: sudo -u postgres psql"

# --- Redis Setup ---
echo "Setting up Redis..."
# By default, Redis runs on localhost (127.0.0.1).
sudo systemctl enable redis-server
sudo systemctl start redis-server
echo "Redis installed and running. You can test with: redis-cli PING"

# --- Python Environment Setup and Application Dependencies ---
echo "Setting up Python virtual environment and installing app dependencies..."

# Define your project directory and virtual environment name
PROJECT_DIR="/home/ubuntu/app/salesAgent" # Adjust this to your project path
VENV_DIR="$PROJECT_DIR/venv"

# Create project directory
sudo mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create a virtual environment
python3 -m venv "$VENV_DIR"

# Activate the virtual environment and install Python packages
# This requires a requirements.txt file in your project directory
echo "Installing Python dependencies (fastapi, langchain, uvicorn, psycopg2-binary, redis, gunicorn)..."
source "$VENV_DIR/bin/activate"

pip install -r requirements.txt
# Install FastAPI, LangChain, Uvicorn, PostgreSQL connector (psycopg2-binary), and Redis library
#pip install "fastapi[standard]" langchain uvicorn psycopg2-binary redis gunicorn

# Deactivate the virtual environment
deactivate

echo "System setup complete. You can now clone your application repository to $PROJECT_DIR"
echo "and configure Gunicorn and Nginx for deployment."


    [Unit]
    Description=My FastAPI Application
    After=network.target

    [Service]
    User=your_username  # Replace with your actual Ubuntu username
    WorkingDirectory=/home/ubuntu/app/sales-agent
    Environment=/home/ubuntu/app/sales-agent/.env
    ExecStart=/home/ubuntu/app/sales-agent/venv/bin/rq worker
    Restart=always

    [Install]
    WantedBy=multi-user.target