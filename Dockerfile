# ─── Stage 1: Build React Frontend ──────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci --silent

COPY frontend/ .
RUN npm run build


# ─── Stage 2: Python Backend + Nginx ────────────────────────────────
FROM python:3.11-slim AS backend

WORKDIR /app

# Install nginx and supervisor
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx supervisor && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built React app to nginx html root
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy configs
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Remove default nginx site
RUN rm -f /etc/nginx/sites-enabled/default

EXPOSE 8080

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
