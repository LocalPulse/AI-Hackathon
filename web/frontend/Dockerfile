FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
RUN npm ci --prefer-offline --no-audit

ARG VITE_API_URL=/api
ARG VITE_USE_MOCK=false

ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_USE_MOCK=${VITE_USE_MOCK}

# Copy source code
COPY . .
RUN npm run build

FROM nginx:alpine

RUN apk add --no-cache wget

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5173 || exit 1

CMD ["nginx", "-g", "daemon off;"]
