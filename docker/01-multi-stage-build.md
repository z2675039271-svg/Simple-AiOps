# Docker 多阶段构建与镜像优化

## 什么是多阶段构建？

多阶段构建允许在一个 Dockerfile 中使用多个 FROM 指令，每个阶段都可以使用不同的基础镜像，最终只保留最后一个阶段的内容。

### 典型对比

**优化前（单阶段）：**
```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["node", "dist/index.js"]
```

**优化后（多阶段）：**
```dockerfile
# 阶段1：构建
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 阶段2：运行
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

## 镜像体积优化技巧

### 1. 使用 Alpine 基础镜像
```dockerfile
FROM python:3.11-alpine
```

### 2. 合并 RUN 指令减少层数
```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*
```

### 3. 利用构建缓存
```dockerfile
# 先复制依赖文件
COPY package*.json ./
RUN npm install
# 再复制代码
COPY . .
```

### 4. .dockerignore 排除不必要文件
```
node_modules
.git
*.log
dist
.env*
```

## 实战：生产级 Node.js 应用 Dockerfile

```dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /build
COPY package*.json ./
RUN npm ci --only=production && \
    npm cache clean --force

COPY . .
RUN npm run build

# 运行阶段
FROM node:20-alpine AS runner
WORKDIR /app

# 创建非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodeapp -u 1001

COPY --from=builder --chown=nodeapp:nodejs /build/dist ./dist
COPY --from=builder --chown=nodeapp:nodejs /build/node_modules ./node_modules

USER nodeapp
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

## 构建最佳实践清单

- [ ] 基础镜像使用 Alpine 或 Distroless
- [ ] 多阶段构建分离编译和运行环境
- [ ] 合并 RUN 指令减少镜像层数
- [ ] 合理使用 .dockerignore
- [ ] 避免安装不必要的工具
- [ ] 使用特定版本而非 latest
- [ ] 配置 HEALTHCHECK 健康检查
- [ ] 以非 root 用户运行容器
