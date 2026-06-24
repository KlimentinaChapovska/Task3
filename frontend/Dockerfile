# --- Build stage ---
FROM node:22-alpine AS builder

WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Production stage — serve static files via Nginx ---
FROM nginx:1.27-alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html

# React Router: send all non-file requests to index.html
COPY nginx/spa.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
