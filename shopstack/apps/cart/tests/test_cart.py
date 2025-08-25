import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app

client = TestClient(app)

def test_add_to_cart_success():
    """Test successful cart addition"""
    cart_item = {
        "product_id": "123",
        "quantity": 2,
        "user_id": "user_456"
    }
    response = client.post("/cart/add", json=cart_item)
    assert response.status_code == 200
    data = response.json()
    assert "cart_id" in data
    assert data["message"] == "Item added to cart successfully"

def test_add_to_cart_invalid_data():
    """Test cart addition with invalid data"""
    cart_item = {
        "product_id": "123",
        "quantity": -1,  # Invalid quantity
        "user_id": "user_456"
    }
    response = client.post("/cart/add", json=cart_item)
    # Should fail validation
    assert response.status_code == 422

def test_get_cart_success():
    """Test successful cart retrieval"""
    # First add an item
    cart_item = {
        "product_id": "456",
        "quantity": 1,
        "user_id": "user_789"
    }
    add_response = client.post("/cart/add", json=cart_item)
    cart_id = add_response.json()["cart_id"]
    
    # Then retrieve the cart
    response = client.get(f"/cart/{cart_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["cart_id"] == cart_id
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == "456"

def test_get_cart_not_found():
    """Test cart not found"""
    response = client.get("/cart/nonexistent_cart")
    assert response.status_code == 404
    assert "Cart not found" in response.json()["detail"]

def test_clear_cart_success():
    """Test successful cart clearing"""
    # First add an item
    cart_item = {
        "product_id": "789",
        "quantity": 3,
        "user_id": "user_123"
    }
    add_response = client.post("/cart/add", json=cart_item)
    cart_id = add_response.json()["cart_id"]
    
    # Then clear the cart
    response = client.delete(f"/cart/{cart_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Cart cleared successfully"
    
    # Verify cart is empty
    get_response = client.get(f"/cart/{cart_id}")
    assert get_response.status_code == 200
    assert len(get_response.json()["items"]) == 0

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
