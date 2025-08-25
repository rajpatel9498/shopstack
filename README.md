# 🛍️ ShopStack - Microservices E-commerce Backend

A production-ready microservices architecture built with Python FastAPI, featuring comprehensive observability, containerization, and Kubernetes deployment with autoscaling.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway  │    │  Catalog Service│    │   Cart Service  │
│   (Port 8000)  │◄──►│   (Port 8001)   │    │   (Port 8002)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  OTel Collector │
                    │   (Port 4317)   │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus   │    │     Grafana     │    │      Loki      │
│  (Port 9090)   │    │   (Port 3000)   │    │   (Port 3100)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │      Tempo      │
                    │   (Port 3200)   │
                    └─────────────────┘
```

## 🚀 Features

### **Core Services**
- **API Gateway**: Reverse proxy with request routing and load balancing
- **Catalog Service**: Product catalog with simulated DB latency (20-60ms)
- **Cart Service**: Shopping cart with simulated write latency (30-90ms) and 1% failure rate

### **Observability Stack**
- **Prometheus**: Metrics collection and storage
- **Grafana**: Dashboards and visualization
- **Loki**: Log aggregation and querying
- **Tempo**: Distributed tracing
- **OpenTelemetry**: Vendor-neutral telemetry instrumentation

### **Infrastructure**
- **Docker**: Multi-stage containerization with <300MB images
- **Docker Compose**: Local development and testing
- **Kubernetes**: Production deployment with Kind cluster
- **HPA**: Horizontal Pod Autoscaler based on CPU/Memory
- **NGINX Ingress**: External traffic routing

## 📁 Project Structure

```
shopstack/
├── apps/                          # Microservices
│   ├── api_gateway/              # API Gateway service
│   │   ├── app.py                # FastAPI application
│   │   ├── Dockerfile            # Multi-stage Docker build
│   │   ├── requirements.txt      # Python dependencies
│   │   └── tests/                # Pytest test suite
│   ├── catalog/                  # Catalog service
│   │   ├── app.py                # FastAPI application
│   │   ├── Dockerfile            # Multi-stage Docker build
│   │   ├── requirements.txt      # Python dependencies
│   │   └── tests/                # Pytest test suite
│   └── cart/                     # Cart service
│       ├── app.py                # FastAPI application
│       ├── Dockerfile            # Multi-stage Docker build
│       ├── requirements.txt      # Python dependencies
│       └── tests/                # Pytest test suite
├── common/                        # Shared modules
│   └── observability.py          # Prometheus metrics + OTel setup
├── ops/                          # Operations and infrastructure
│   ├── k8s/                      # Kubernetes manifests
│   │   ├── namespace.yaml        # ShopStack namespace
│   │   ├── configmap.yaml        # Environment configuration
│   │   ├── *-deployment.yaml     # Service deployments
│   │   ├── hpa.yaml              # Horizontal Pod Autoscalers
│   │   ├── ingress.yaml          # NGINX ingress configuration
│   │   └── load-test.sh          # Load testing script
│   ├── kind/                     # Local Kubernetes cluster
│   │   └── cluster-config.yaml   # Kind cluster configuration
│   ├── grafana/                  # Grafana provisioning
│   │   ├── provisioning/
│   │   │   ├── dashboards/       # Dashboard configurations
│   │   │   └── datasources/      # Data source configurations
│   ├── prometheus/               # Prometheus configuration
│   │   └── prometheus.yml        # Scrape configuration
│   ├── loki/                     # Loki configuration
│   │   ├── local-config.yaml     # Loki server configuration
│   │   └── entrypoint.sh         # Custom entrypoint script
│   ├── promtail/                 # Promtail configuration
│   │   └── config.yml            # Log collection configuration
│   ├── tempo/                    # Tempo configuration
│   │   └── tempo.yaml            # Trace storage configuration
│   └── otel-collector/           # OpenTelemetry Collector
│       └── config.yaml           # Telemetry routing configuration
├── docker-compose.yaml            # Local development stack
├── Makefile                      # Build and deployment automation
├── requirements.txt               # Global Python dependencies
└── README.md                     # This file
```

## 🛠️ Quick Start

### **Prerequisites**
- Python 3.12+
- Docker & Docker Compose
- Make
- Kind (for local Kubernetes)
- kubectl

### **Local Development (Docker Compose)**

1. **Clone and setup:**
   ```bash
   git clone <your-repo-url>
   cd shopstack
   make install
   ```

2. **Start the full stack:**
   ```bash
   make compose-up
   ```

3. **Access services:**
   - API Gateway: http://localhost:8000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)
   - Loki: http://localhost:3100
   - Tempo: http://localhost:3200

4. **Test the API:**
   ```bash
   # Health check
   curl http://localhost:8000/healthz
   
   # Browse catalog
   curl http://localhost:8000/catalog/123
   
   # Add to cart
   curl -X POST http://localhost:8000/cart/add \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user123", "product_id": "123", "quantity": 2}'
   ```

5. **Stop the stack:**
   ```bash
   make compose-down
   ```

### **Local Kubernetes (Kind)**

1. **Create Kind cluster:**
   ```bash
   kind create cluster --config ops/kind/cluster-config.yaml
   ```

2. **Install metrics server:**
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
   ```

3. **Deploy to Kubernetes:**
   ```bash
   # Load Docker images
   kind load docker-image shopstack_catalog:latest shopstack_cart:latest shopstack_api_gateway:latest --name shopstack-cluster
   
   # Deploy services
   kubectl apply -f ops/k8s/
   ```

4. **Test autoscaling:**
   ```bash
   # Port forward to API gateway
   kubectl port-forward -n shopstack service/api-gateway 8080:8000 &
   
   # Run load test
   ./ops/k8s/load-test.sh
   
   # Monitor scaling
   kubectl get hpa -n shopstack -w
   ```

## 🔧 Development

### **Running Tests**
```bash
# Run all tests
make test-all

# Run specific service tests
make test-catalog
make test-cart
make test-gateway
```

### **Building Docker Images**
```bash
# Build all images
make docker-build

# Build specific service
make docker-build-catalog
make docker-build-cart
make docker-build-gateway
```

### **Local Service Development**
```bash
# Start individual services
make run-catalog
make run-cart
make run-gateway

# Start all services
make run-all
```

## 📊 Monitoring & Observability

### **Metrics (Prometheus)**
- HTTP request counts and durations
- Service health and readiness
- Resource utilization (CPU, Memory)

### **Logs (Loki)**
- Structured JSON logging
- Trace and span correlation
- Centralized log aggregation

### **Traces (Tempo)**
- Distributed request tracing
- Service dependency mapping
- Performance bottleneck identification

### **Dashboards (Grafana)**
- Pre-configured FastAPI dashboards
- Service metrics visualization
- Log and trace correlation views

## 🚀 Production Deployment

### **AWS EKS (Coming Soon)**
- Terraform infrastructure as code
- EKS cluster with autoscaling
- ECR container registry
- Application Load Balancer
- CloudWatch monitoring

### **Helm Charts (Coming Soon)**
- Kubernetes application packaging
- Environment-specific configurations
- CI/CD pipeline integration

## 🧪 Load Testing

### **Locust Integration**
```bash
# Run Locust load tests
cd ops
locust -f locustfile.py --host=http://localhost:8000
```

### **Custom Load Testing**
```bash
# Run the built-in load test
./ops/k8s/load-test.sh
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Port conflicts:**
   ```bash
   # Check what's using a port
   sudo lsof -i :8000
   
   # Kill processes if needed
   sudo kill -9 <PID>
   ```

2. **Docker permission issues:**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Restart terminal session
   ```

3. **Kubernetes metrics server:**
   ```bash
   # Check metrics server status
   kubectl get pods -n kube-system | grep metrics-server
   
   # View logs
   kubectl logs -n kube-system <metrics-server-pod>
   ```

### **Useful Commands**
```bash
# Check service status
docker-compose ps
kubectl get all -n shopstack

# View logs
docker-compose logs <service>
kubectl logs -n shopstack <pod-name>

# Monitor resources
kubectl top pods -n shopstack
kubectl get hpa -n shopstack
```

## 📈 Performance Characteristics

### **Service Latencies**
- **Catalog Service**: 20-60ms (simulated DB read)
- **Cart Service**: 30-90ms (simulated DB write)
- **API Gateway**: <5ms (proxy overhead)

### **Failure Rates**
- **Catalog Service**: 0% (read-only)
- **Cart Service**: 1% (simulated failures)
- **API Gateway**: 0% (proxy only)

### **Scaling Thresholds**
- **CPU**: 70% utilization
- **Memory**: 80% utilization
- **Min Replicas**: 2
- **Max Replicas**: 10

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Prometheus, Grafana, Loki, and Tempo for observability
- Kubernetes community for the amazing orchestration platform
- OpenTelemetry for vendor-neutral telemetry standards

---

**Built with ❤️ for learning microservices, observability, and cloud-native development**
