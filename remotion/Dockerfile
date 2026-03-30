FROM node:20-slim

WORKDIR /app

# Install Chrome deps for Remotion rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium fonts-noto-cjk fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Node deps
COPY package.json package-lock.json* ./
RUN npm ci

# App code
COPY src/ src/
COPY tsconfig.json ./

# Public dir will be mounted as volume
RUN mkdir -p public outputs

EXPOSE 3334

CMD ["npx", "remotion", "studio", "--port", "3334", "--disable-keyboard-shortcuts"]
