.PHONY: help install test test-catalog test-cart test-gateway run-catalog run-cart run-gateway run-all load-test clean docker-build compose-up compose-down docker-clean

# Default target
help:
	@echo "ShopStack Microservices - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install          Install all dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-catalog     Run catalog service tests"
	@echo "  test-cart        Run cart service tests"
	@echo "  test-gateway     Run API gateway tests"
	@echo ""
	@echo "Running Services:"
	@echo "  run-catalog      Start catalog service on port 8001"
	@echo "  run-cart         Start cart service on port 8002"
	@echo "  run-gateway      Start API gateway on port 8000"
	@echo "  run-all          Start all services in background"
	@echo ""
	@echo "Load Testing:"
	@echo "  load-test        Run Locust load testing against gateway"
	@echo ""
	@echo "Docker & Compose:"
	@echo "  docker-build     Build all Docker images"
	@echo "  compose-up       Start full stack with Docker Compose"
	@echo "  compose-down     Stop Docker Compose stack"
	@echo "  docker-clean     Clean up Docker resources"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            Stop all services and clean up"
	@echo "  status           Show status of running services"

# Install dependencies
install:
	@echo "Installing dependencies for all services..."
	@echo "Activating virtual environment..."
	. venv/bin/activate && pip install -r apps/catalog/requirements.txt
	. venv/bin/activate && pip install -r apps/cart/requirements.txt
	. venv/bin/activate && pip install -r apps/api_gateway/requirements.txt
	. venv/bin/activate && pip install pytest locust

# Run tests
test: test-catalog test-cart test-gateway

test-catalog:
	@echo "Running catalog service tests..."
	cd apps/catalog && ../../venv/bin/pytest tests/ -v

test-cart:
	@echo "Running cart service tests..."
	cd apps/cart && ../../venv/bin/pytest tests/ -v

test-gateway:
	@echo "Running API gateway tests..."
	cd apps/api_gateway && ../../venv/bin/pytest tests/ -v

# Run services
run-catalog:
	@echo "Starting catalog service on port 8001..."
	cd apps/catalog && ../venv/bin/python3 app.py

run-cart:
	@echo "Starting cart service on port 8002..."
	cd apps/cart && ../venv/bin/python3 app.py

run-gateway:
	@echo "Starting API gateway on port 8000..."
	cd apps/api_gateway && ../venv/bin/python3 app.py

# Run all services in background
run-all:
	@echo "Starting all services..."
	@echo "Catalog service will run on port 8001"
	@echo "Cart service will run on port 8002"
	@echo "API Gateway will run on port 8000"
	@echo ""
	@echo "Use 'make status' to check service status"
	@echo "Use 'make clean' to stop all services"
	@echo ""
	cd apps/catalog && nohup ../../venv/bin/python3 app.py > ../catalog.log 2>&1 & echo $$! > ../catalog.pid
	cd apps/cart && nohup ../../venv/bin/python3 app.py > ../cart.log 2>&1 & echo $$! > ../cart.pid
	cd apps/api_gateway && nohup ../../venv/bin/python3 app.py > ../gateway.log 2>&1 & echo $$! > ../gateway.pid
	@echo "All services started. Waiting for them to be ready..."
	@sleep 3
	@echo "Testing gateway endpoint..."
	@curl -s http://localhost:8000/ | grep -q "API Gateway" && echo "✅ Gateway is ready!" || echo "❌ Gateway not ready yet"

# Load testing
load-test:
	@echo "Starting Locust load testing..."
	@echo "Target: http://localhost:8000"
	@echo "Open http://localhost:8089 in your browser to view results"
	cd ops && locust -f locustfile.py --host=http://localhost:8000

# Docker commands
docker-build:
	@echo "Building all Docker images..."
	docker-compose build

compose-up:
	@echo "Starting full stack with Docker Compose..."
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services should be available at:"
	@echo "  - API Gateway: http://localhost:8000"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3000 (admin/admin)"
	@echo "  - Loki: http://localhost:3100"
	@echo "  - Tempo: http://localhost:3200"

compose-down:
	@echo "Stopping Docker Compose stack..."
	docker-compose down

docker-clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Show service status
status:
	@echo "Service Status:"
	@echo "==============="
	@if [ -f apps/catalog.pid ]; then \
		echo "Catalog Service: $$(ps -p $$(cat apps/catalog.pid) >/dev/null 2>&1 && echo "Running (PID: $$(cat apps/catalog.pid))" || echo "Not running")"; \
	else \
		echo "Catalog Service: Not started"; \
	fi
	@if [ -f apps/cart.pid ]; then \
		echo "Cart Service: $$(ps -p $$(cat apps/cart.pid) >/dev/null 2>&1 && echo "Running (PID: $$(cat apps/cart.pid))" || echo "Not running")"; \
	else \
		echo "Cart Service: Not started"; \
	fi
	@if [ -f apps/api_gateway.pid ]; then \
		echo "API Gateway: $$(ps -p $$(cat apps/api_gateway.pid) >/dev/null 2>&1 && echo "Running (PID: $$(cat apps/api_gateway.pid))" || echo "Not running")"; \
	else \
		echo "API Gateway: Not started"; \
	fi
	@echo ""
	@echo "Port Status:"
	@echo "============"
	@echo "Port 8000 (Gateway): $$(netstat -tlnp 2>/dev/null | grep :8000 || echo "Not listening")"
	@echo "Port 8001 (Catalog): $$(netstat -tlnp 2>/dev/null | grep :8001 || echo "Not listening")"
	@echo "Port 8002 (Cart): $$(netstat -tlnp 2>/dev/null | grep :8002 || echo "Not listening")"

# Clean up
clean:
	@echo "Stopping all services..."
	@if [ -f apps/catalog.pid ]; then \
		kill $$(cat apps/catalog.pid) 2>/dev/null || true; \
		rm -f apps/catalog.pid; \
		echo "Catalog service stopped"; \
	fi
	@if [ -f apps/cart.pid ]; then \
		kill $$(cat apps/cart.pid) 2>/dev/null || true; \
		rm -f apps/cart.pid; \
		echo "Cart service stopped"; \
	fi
	@if [ -f apps/api_gateway.pid ]; then \
		kill $$(cat apps/api_gateway.pid) 2>/dev/null || true; \
		rm -f apps/api_gateway.pid; \
		echo "API Gateway stopped"; \
	fi
	@echo "Cleaning up log files..."
	@rm -f apps/*.log
	@echo "All services stopped and cleaned up"

# Quick test endpoints
test-endpoints:
	@echo "Testing service endpoints..."
	@echo "Testing catalog service..."
	@curl -s http://localhost:8001/healthz | grep -q "healthy" && echo "✅ Catalog health OK" || echo "❌ Catalog health failed"
	@echo "Testing cart service..."
	@curl -s http://localhost:8002/healthz | grep -q "healthy" && echo "✅ Cart health OK" || echo "❌ Cart health failed"
	@echo "Testing API gateway..."
	@curl -s http://localhost:8000/healthz | grep -q "healthy" && echo "✅ Gateway health OK" || echo "❌ Gateway health failed"
	@echo ""
	@echo "Testing catalog through gateway..."
	@curl -s http://localhost:8000/catalog/123 | grep -q "Wireless Headphones" && echo "✅ Catalog proxy OK" || echo "❌ Catalog proxy failed"
	@echo ""
	@echo "Testing metrics endpoint..."
	@curl -s http://localhost:8000/metrics | grep -q "http_requests_total" && echo "✅ Metrics OK" || echo "❌ Metrics failed"
