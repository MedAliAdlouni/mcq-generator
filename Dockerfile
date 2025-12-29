FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# for gunicorn installation
ENV PATH="/root/.local/bin:$PATH"

# Copy only dependency files first to leverage build cache
COPY pyproject.toml uv.lock ./

# Install dependencies exactly as locked
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Then copy the rest of your project
COPY . .

# Expose port
EXPOSE 5000

# Run via uv (automatically uses .venv)
CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
