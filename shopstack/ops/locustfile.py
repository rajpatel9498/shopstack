import random
import json
from locust import HttpUser, task, between

class EcommerceUser(HttpUser):
    """Simulates an e-commerce user browsing catalog and adding items to cart"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Initialize user session"""
        self.user_id = f"user_{random.randint(1000, 9999)}"
        self.cart_id = None
    
    @task(7)  # 70% probability - catalog browsing
    def browse_catalog(self):
        """Browse catalog - get product details"""
        # Randomly select from available product IDs
        product_ids = ["123", "456", "789"]
        product_id = random.choice(product_ids)
        
        with self.client.get(f"/catalog/{product_id}", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == product_id:
                    response.success()
                else:
                    response.failure(f"Expected product ID {product_id}, got {data.get('id')}")
            else:
                response.failure(f"Expected 200, got {response.status_code}")
    
    @task(3)  # 30% probability - add to cart
    def add_to_cart(self):
        """Add item to cart"""
        # Randomly select from available product IDs
        product_ids = ["123", "456", "789"]
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 5)
        
        cart_item = {
            "product_id": product_id,
            "quantity": quantity,
            "user_id": self.user_id
        }
        
        with self.client.post("/cart/add", 
                            json=cart_item, 
                            catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "cart_id" in data and data.get("message") == "Item added to cart successfully":
                    response.success()
                    # Store cart ID for potential future use
                    if not self.cart_id:
                        self.cart_id = data.get("cart_id")
                else:
                    response.failure(f"Unexpected response format: {data}")
            elif response.status_code == 500:
                # This is expected due to 1% failure rate simulation
                response.success()
            else:
                response.failure(f"Expected 200 or 500, got {response.status_code}")
    
    @task(1)  # 10% probability - list all products
    def list_products(self):
        """List all available products"""
        with self.client.get("/catalog", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    response.success()
                else:
                    response.failure(f"Expected non-empty list, got {data}")
            else:
                response.failure(f"Expected 200, got {response.status_code}")
    
    @task(1)  # 10% probability - health check
    def health_check(self):
        """Check service health"""
        with self.client.get("/healthz", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure(f"Expected healthy status, got {data}")
            else:
                response.failure(f"Expected 200, got {response.status_code}")

class MetricsUser(HttpUser):
    """Simulates monitoring/observability requests"""
    
    wait_time = between(10, 30)  # Less frequent monitoring requests
    
    @task(1)
    def get_metrics(self):
        """Get Prometheus metrics"""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                if "http_requests_total" in response.text:
                    response.success()
                else:
                    response.failure("Metrics endpoint not returning expected data")
            else:
                response.failure(f"Expected 200, got {response.status_code}")
    
    @task(1)
    def get_livez(self):
        """Check liveness"""
        with self.client.get("/livez", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "alive":
                    response.success()
                else:
                    response.failure(f"Expected alive status, got {data}")
            else:
                response.failure(f"Expected 200, got {response.status_code}")
