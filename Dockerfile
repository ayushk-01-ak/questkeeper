# Dockerfile
# Recipe for building the QuestKeeper container

# Start from official Python 3.11 slim image
# "slim" means minimal OS — smaller download, faster builds
FROM python:3.11-slim

# Set working directory inside the container
# All subsequent commands run from here
WORKDIR /app

# Copy requirements first — before copying source code
# Why? Docker caches layers. If requirements haven't changed,
# Docker skips reinstalling packages on rebuild.
# This makes rebuilds much faster during development.
COPY requirements.txt .

# Install Python packages
# --no-cache-dir keeps the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the source code
COPY . .

# Create directories that need to exist at runtime
RUN mkdir -p data chroma_store

# Expose ports so the outside world can reach our services
EXPOSE 8000
EXPOSE 8501

# Default command — overridden by docker-compose
CMD ["echo", "Use docker compose up instead"]