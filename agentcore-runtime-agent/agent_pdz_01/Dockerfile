# Use uv's ARM64 Python base image (required by AgentCore)
FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy agent code
COPY agent.py ./

# Expose port 8080 (AgentCore requirement)
EXPOSE 8080

# Run the FastAPI application
# Use python -m uvicorn instead of uv run to avoid package build issues
CMD [".venv/bin/python", "-m", "uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8080"]
