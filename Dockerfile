FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app

# Run the MCP server using uv
CMD ["uv", "run", "python", "-m", "src.server"]
