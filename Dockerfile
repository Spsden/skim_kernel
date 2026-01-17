# =============================================================================
# SKIM KERNEL - Dockerfile with UV
# =============================================================================
# Multi-stage build for optimal layer caching and minimal image size
# =============================================================================

FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV - Fast Python package installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# =============================================================================
# DEPENDENCIES STAGE
# =============================================================================
FROM base AS dependencies

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies with UV (faster than pip)
RUN uv sync --frozen --no-dev

# =============================================================================
# DEVELOPMENT STAGE
# =============================================================================
FROM dependencies AS development

# Install development dependencies
RUN uv sync --frozen --all-extras

# Copy source code
COPY . .

# Set the default command
CMD ["/bin/bash"]

# =============================================================================
# PRODUCTION STAGE
# =============================================================================
FROM base AS production

# Copy dependencies from dependencies stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy application code
COPY . .

# Ensure Python uses the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Create non-root user for running the application
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden)
CMD ["python", "main.py", "amarkantak"]

# =============================================================================
# ENTRYPOINT VARIANTS
# =============================================================================
# To run different services:
#   docker run skim-kernel:latest kalinga      # RSS feed service
#   docker run skim-kernel:latest bundelkhand  # Scraping service
#   docker run skim-kernel:latest amarkantak   # Summarization service
#   docker run skim-kernel:latest mahabharat   # All services
