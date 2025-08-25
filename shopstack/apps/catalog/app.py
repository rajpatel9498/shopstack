import os
import random
import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add parent directory to path to import common module
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.observability import add_observability_routes, setup_otel_instrumentation

# Setup logging
logger = logging.getLogger(__name__)

# Setup OpenTelemetry if configured
setup_otel_instrumentation()

app = FastAPI(title="Catalog Service", version="1.0.0")

# Add observability routes
add_observability_routes(app)

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str

# Simulate product database
PRODUCTS = {
    "123": Product(
        id="123",
        name="Wireless Headphones",
        description="High-quality wireless headphones with noise cancellation",
        price=199.99,
        category="Electronics"
    ),
    "456": Product(
        id="456",
        name="Smart Watch",
        description="Feature-rich smartwatch with health monitoring",
        price=299.99,
        category="Electronics"
    ),
    "789": Product(
        id="789",
        name="Running Shoes",
        description="Comfortable running shoes for all terrains",
        price=89.99,
        category="Sports"
    )
}

@app.get("/catalog/{product_id}")
async def get_product(product_id: str):
    """Get product by ID with simulated database read latency"""
    logger.info(f"Fetching product {product_id}")
    
    # Simulate database read latency (20-60ms)
    latency = random.uniform(0.02, 0.06)
    time.sleep(latency)
    
    if product_id not in PRODUCTS:
        logger.warning(f"Product {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = PRODUCTS[product_id]
    logger.info(f"Successfully retrieved product {product_id}: {product.name}")
    
    return product

@app.get("/catalog")
async def list_products():
    """List all products"""
    logger.info("Listing all products")
    return list(PRODUCTS.values())

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
