# Use UV's official Python 3.13 image
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY . .

# Install project
RUN uv sync --frozen --no-dev

# ============================================
# Backend target
# ============================================
FROM base AS backend

EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================
# Frontend target  
# ============================================
FROM base AS frontend

EXPOSE 8501

# Run Streamlit
CMD ["uv", "run", "streamlit", "run", "frontend/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
