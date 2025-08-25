import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint with service information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "API Gateway"
    assert data["version"] == "1.0.0"
    assert "catalog_service" in data
    assert "cart_service" in data
    assert "endpoints" in data

def test_healthz():
    """Test health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_livez():
    """Test liveness check endpoint"""
    response = client.get("/livez")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_metrics():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text

# Note: Integration tests for proxying to catalog/cart services
# would require running those services or mocking them
# These tests focus on the gateway's own endpoints
