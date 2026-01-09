FROM python:3.11-slim

# Install Node.js 22.x
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js version
RUN node --version && npm --version

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN uv sync --frozen

# Build frontend
WORKDIR /app/frontend
RUN npm install --legacy-peer-deps && npm run build

# Go back to app directory
WORKDIR /app

# Expose port (Render provides $PORT env var)
EXPOSE 8002

# Run the application (Render will set $PORT)
CMD uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8002}

