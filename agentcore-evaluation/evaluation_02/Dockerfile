FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agent.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV USE_MCP_ARN=true

# Expose port (AgentCore runtime doesn't need this, but kept for compatibility)
EXPOSE 8080

# Run the agent
CMD ["python", "agent.py"]
