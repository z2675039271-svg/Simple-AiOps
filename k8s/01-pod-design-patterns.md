# Kubernetes Pod 设计模式

## 1. Init Container 模式

Init Container 在应用容器之前运行，常用于：
- 等待依赖服务就绪
- 预拉取配置或数据
- 初始化数据库

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  initContainers:
    - name: wait-for-db
      image: busybox:1.36
      command:
        - sh
        - -c
        - |
          echo "Waiting for database..."
          until nc -z db-service 5432; do
            echo "Database not ready, retrying..."
            sleep 2
          done
          echo "Database is ready!"

    - name: fetch-config
      image: curlimages/curl:latest
      command:
        - sh
        - -c
        - |
          curl -s http://config-server/config | tee /config/app.yaml

  containers:
    - name: app
      image: my-app:v1
      volumeMounts:
        - name: config
          mountPath: /config
```

## 2. Sidecar 模式

Sidecar 增强主容器能力：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server
spec:
  containers:
    - name: main-app
      image: nginx:alpine
      ports:
        - containerPort: 80
      volumeMounts:
        - name: shared-logs
          mountPath: /var/log/nginx

    # 日志收集 Sidecar
    - name: log-collector
      image: busybox:1.36
      command: ["sh", "-c", "tail -f /var/log/nginx/access.log"]
      volumeMounts:
        - name: shared-logs
          mountPath: /var/log/nginx

    # 代理 Sidecar
    - name: proxy-sidecar
      image: envoyproxy/envoy:latest
      ports:
        - containerPort: 9901
```

## 3. Ambassador 模式

通过代理简化外部服务访问：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-cache
spec:
  containers:
    - name: app
      image: my-app:v1
      env:
        - name: REDIS_HOST
          value: "localhost"

    - name: redis-proxy
      image: redis:7-alpine
      command: ["redis-server", "--port", "6379"]
      ports:
        - containerPort: 6379
```

## 4. Adapter 模式

统一输出格式：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-adapter
spec:
  containers:
    - name: main-app
      image: my-app:v1
      ports:
        - containerPort: 8080

    - name: prometheus-adapter
      image: prometheus/adapter:latest
      args:
        - --config.file=/etc/adapter/config.yaml
        - --logtostderr=true
        - --metrics-relay=localhost:8080/metrics
```

## 生命周期管理

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: lifecycle-demo
spec:
  containers:
    - name: app
      image: nginx:alpine
      lifecycle:
        postStart:
          exec:
            command: ["/bin/sh", "-c", "echo 'Container started' > /tmp/started"]
        preStop:
          exec:
            command: ["/bin/sh", "-c", "nginx -s quit; sleep 5"]
      readinessProbe:
        httpGet:
          path: /healthz
          port: 80
        initialDelaySeconds: 5
        periodSeconds: 10
      livenessProbe:
        tcpSocket:
          port: 80
        initialDelaySeconds: 15
        periodSeconds: 20
```
