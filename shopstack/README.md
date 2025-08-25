# 🛍️ ShopStack - Microservice E-commerce Backend

A hands-on project simulating a realistic microservice-based e-commerce backend using **Python (FastAPI)** with comprehensive observability, testing, and load testing capabilities.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway  │    │   Catalog       │    │   Cart          │
│   (Port 8000)  │◄──►│   Service       │    │   Service       │
│                 │    │   (Port 8001)   │    │   (Port 8002)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Observability │
                    │   (Prometheus   │
                    │   + OTel)      │
                    └─────────────────┘
```

## 🚀 Features

### Services
- **API Gateway**: Routes requests to backend services
- **Catalog Service**: Product catalog with simulated DB read latency (20-60ms)
- **Cart Service**: Shopping cart with simulated write latency (30-90ms) and 1% failure rate

### Observability
- **Prometheus Metrics**: Request counts, latency histograms, status codes
- **OpenTelemetry**: Distributed tracing (when OTLP endpoint configured)
- **Structured Logging**: JSON format with trace correlation
- **Health Checks**: `/healthz`, `/livez`, `/metrics` endpoints

### Testing & Load Testing
- **Unit Tests**: pytest-based tests for each service
- **Load Testing**: Locust-based simulation (70% catalog browsing, 30% cart operations)

## 📁 Project Structure

```
shopstack/
├── apps/
│   ├── api_gateway/          # API Gateway service
│   │   ├── app.py           # Main application
│   │   ├── requirements.txt  # Dependencies
│   │   └── tests/           # Test files
│   ├── catalog/             # Catalog service
│   │   ├── app.py           # Main application
│   │   ├── requirements.txt  # Dependencies
│   │   └── tests/           # Test files
│   └── cart/                # Cart service
│       ├── app.py           # Main application
│       ├── requirements.txt  # Dependencies
│       └── tests/           # Test files
├── common/
│   └── observability.py     # Shared observability utilities
├── ops/
│   └── locustfile.py        # Load testing scenarios
├── Makefile                 # Build and run commands
└── README.md               # This file
```

## 🛠️ Quick Start

### Option 1: Local Development (Milestone 1)

#### 1. Install Dependencies

```bash
make install
```

#### 2. Run All Services

```bash
make run-all
```

This starts:
- Catalog service on port 8001
- Cart service on port 8002  
- API Gateway on port 8000

### Option 2: Docker Compose with Full Observability Stack (Milestones 3 & 4)

#### 1. Build Docker Images

```bash
make docker-build
```

#### 2. Start Full Stack

```bash
make compose-up
```

This starts:
- **Application Services**: API Gateway (8000), Catalog (8001), Cart (8002)
- **Observability Stack**: Prometheus (9090), Grafana (3000), Loki (3100), Tempo (3200)
- **OTel Collector**: Receives traces, metrics, and logs from all services

### 3. Test the System

```bash
# Test all endpoints
make test-endpoints

# Run all tests
make test

# Check service status
make status
```

### 4. Load Testing

```bash
make load-test
```

Open http://localhost:8089 in your browser to view Locust results.

## 🔧 Individual Service Commands

### Start Individual Services

```bash
# Start catalog service only
make run-catalog

# Start cart service only  
make run-cart

# Start API gateway only
make run-gateway
```

### Run Individual Tests

```bash
# Test catalog service
make test-catalog

# Test cart service
make test-cart

# Test API gateway
make test-gateway
```

## 📊 API Endpoints

### API Gateway (Port 8000)
- `GET /` - Service information
- `GET /catalog/{id}` - Get product (proxied to catalog service)
- `POST /cart/add` - Add item to cart (proxied to cart service)
- `GET /cart/{id}` - Get cart contents (proxied to cart service)
- `DELETE /cart/{id}` - Clear cart (proxied to cart service)

### Catalog Service (Port 8001)
- `GET /catalog/{id}` - Get product by ID
- `GET /catalog` - List all products

### Cart Service (Port 8002)
- `POST /cart/add` - Add item to cart
- `GET /cart/{id}` - Get cart contents
- `DELETE /cart/{id}` - Clear cart

### All Services
- `GET /healthz` - Health check
- `GET /livez` - Liveness check
- `GET /metrics` - Prometheus metrics

## 🔍 Observability

### Prometheus Metrics
- `http_requests_total` - Total request count by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram

### OpenTelemetry
Enable distributed tracing by setting the `OTLP_ENDPOINT` environment variable:

```bash
export OTLP_ENDPOINT=http://localhost:4317
```

### Logging
All services log in JSON format with:
- Request/response details
- Trace and span IDs (when OTel enabled)
- Timing information
- Error details

## 🧪 Testing

### Test Coverage
- **Catalog Service**: Product retrieval, error handling, health checks
- **Cart Service**: Add/remove items, error handling, health checks  
- **API Gateway**: Proxying, health checks, metrics

### Running Tests
```bash
# Run all tests
make test

# Run specific service tests
make test-catalog
make test-cart
make test-gateway
```

## 📈 Load Testing

### Locust Scenarios
- **EcommerceUser** (70% catalog browsing, 30% cart operations)
- **MetricsUser** (monitoring requests)

### Load Test Commands
```bash
# Start load testing
make load-test

# View results at http://localhost:8089
```

## 🐳 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | 8000 (gateway), 8001 (catalog), 8002 (cart) |
| `CATALOG_SERVICE_URL` | Catalog service URL | http://localhost:8001 |
| `CART_SERVICE_URL` | Cart service URL | http://localhost:8002 |
| `OTLP_ENDPOINT` | OpenTelemetry OTLP endpoint | (disabled) |

## 🧹 Cleanup

### Local Development
```bash
# Stop all services and clean up
make clean
```

### Docker Compose
```bash
# Stop the stack
make compose-down

# Clean up Docker resources
make docker-clean
```

## 🔮 Next Steps (Future Milestones)

- **✅ Milestone 1**: Local FastAPI services with observability (COMPLETE)
- **✅ Milestone 2**: Containerization with Docker (COMPLETE)
- **✅ Milestone 3**: Docker Compose with local observability stack (COMPLETE)
- **✅ Milestone 4**: Infrastructure as Code with Terraform (COMPLETE)
- **🔄 Milestone 5**: Kubernetes deployment with Helm (NEXT)
- **🔄 Milestone 6**: Production observability stack on cloud infrastructure

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Use `make clean` to stop all services
2. **Import errors**: Ensure you're in the `shopstack` directory
3. **Service not responding**: Check logs in `apps/*.log` files
4. **Tests failing**: Ensure all services are running with `make status`

### Debug Commands

```bash
# Check service status
make status

# View logs
tail -f apps/catalog.log
tail -f apps/cart.log  
tail -f apps/gateway.log

# Test endpoints manually
curl http://localhost:8000/healthz
curl http://localhost:8000/catalog/123
curl http://localhost:8000/metrics
```

## 📝 Development

### Adding New Endpoints
1. Add route to service `app.py`
2. Add test in `tests/` directory
3. Update load testing if needed
4. Test with `make test`

### Adding New Services
1. Create service directory in `apps/`
2. Copy and modify existing service structure
3. Update Makefile commands
4. Add to load testing scenarios

## 🤝 Contributing

This is a learning project. Feel free to:
- Add new features
- Improve observability
- Enhance load testing scenarios
- Optimize performance
- Add more comprehensive tests

---

**Happy coding! 🚀**
