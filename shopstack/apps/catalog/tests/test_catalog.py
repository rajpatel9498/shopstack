import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app

client = TestClient(app)

def test_get_product_success():
    """Test successful product retrieval"""
    response = client.get("/catalog/123")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert data["name"] == "Wireless Headphones"
    assert data["price"] == 199.99

def test_get_product_not_found():
    """Test product not found"""
    response = client.get("/catalog/999")
    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]

def test_list_products():
    """Test listing all products"""
    response = client.get("/catalog")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 3
    assert any(p["id"] == "123" for p in products)
    assert any(p["id"] == "456" for p in products)
    assert any(p["id"] == "789" for p in products)

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
