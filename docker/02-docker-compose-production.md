# Docker Compose 生产级配置

## 健康检查与依赖管理

```yaml
version: '3.8'
services:
  app:
    build: .
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: admin
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass-file /run/secrets/redis_password
    secrets:
      - redis_password

volumes:
  postgres_data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
  redis_password:
    file: ./secrets/redis_password.txt
```

## 资源限制配置

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 256M

  worker:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

## 日志驱动优化

```yaml
version: '3.8'
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"
        compress: "true"
```

## 网络配置

```yaml
networks:
  frontend:
  backend:
    driver: bridge

services:
  app:
    networks:
      - frontend
      - backend
    ports:
      - "8080:3000"

  nginx:
    networks:
      - frontend
    ports:
      - "80:80"
```

## 重启策略

```yaml
services:
  app:
    restart: unless-stopped  # 生产推荐
    # restart: always        # 容器崩溃自动重启
    # restart: on-failure    # 仅失败时重启
```
