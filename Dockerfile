FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

# Python deps
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# App code
COPY src/ src/
COPY configs/ configs/
COPY scripts/ scripts/

# Volumes will mount these at runtime
RUN mkdir -p remotion/public outputs data

EXPOSE 8800

CMD ["uv", "run", "python", "-m", "seasonxi.api.server"]
