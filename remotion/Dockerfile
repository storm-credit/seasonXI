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
COPY render-server.js ./

# Public dir will be mounted as volume
RUN mkdir -p public outputs

EXPOSE 3334 3335

# Run both Remotion Studio + Render Server
CMD ["sh", "-c", "node render-server.js & npx remotion studio --port 3334 --disable-keyboard-shortcuts"]
