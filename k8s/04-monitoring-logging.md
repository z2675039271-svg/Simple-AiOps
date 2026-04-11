# Kubernetes 监控与日志收集

## Prometheus + Grafana 部署

### Prometheus 配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
        relabel_configs:
          - source_labels: [__address__]
            regex: '([^:]+):\d+'
            target_label: __address__
            replacement: '\1:10250'

      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_name]
            action: keep
            regex: .+

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:latest
          args:
            - '--config.file=/etc/prometheus/prometheus.yml'
            - '--storage.tsdb.path=/prometheus'
            - '--web.enable-lifecycle'
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
            - name: storage
              mountPath: /prometheus
      volumes:
        - name: config
          configMap:
            name: prometheus-config
        - name: storage
          emptyDir: {}
```

## Loki 日志收集

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: monitoring
data:
  promtail.yaml: |
    server:
      http_listen_port: 9080
      grpc_listen_port: 0

    positions:
      filename: /tmp/positions.yaml

    client:
      url: http://loki:3100/loki/api/v1/push

    scrape_configs:
      - job_name: kubernetes-pods
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
```

## 自定义指标告警规则

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: custom-alerts
  namespace: monitoring
spec:
  groups:
    - name: app-alerts
      rules:
        - alert: HighCPUUsage
          expr: rate(container_cpu_usage_seconds_total{container!=""}[5m]) > 0.8
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High CPU Usage on {{ $labels.pod }}"
            description: "CPU usage is above 80% for 5 minutes"

        - alert: OOMKilled
          expr: kube_pod_container_status_restarts_total{reason="OOMKilled"} > 0
          for: 1m
          labels:
            severity: critical
          annotations:
            summary: "Pod {{ $labels.pod }} OOM Killed"
            description: "Container was OOM Killed"

        - alert: PodNotReady
          expr: kube_pod_status_ready{condition="true"} == 0
          for: 10m
          labels:
            severity: warning
```

## 日志查询示例（Loki + Grafana）

```logql
# 错误日志统计
sum by (namespace, pod) (rate({app="my-app"} |~ "ERROR" [5m]))

# 最近1小时的日志
{namespace="production", app="my-app"} |= "error" | json | line_format "{{.timestamp}} {{.message}}"

# 追踪特定请求
{kubernetes_pod_name=~"api.*"} |~ "request_id=abc123"
```
