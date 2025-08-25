import os
import logging
import httpx
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

app = FastAPI(title="API Gateway", version="1.0.0")

# Add observability routes
add_observability_routes(app)

# Service URLs from environment variables
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8001")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://localhost:8002")

logger.info(f"Catalog service URL: {CATALOG_SERVICE_URL}")
logger.info(f"Cart service URL: {CART_SERVICE_URL}")

class CartItem(BaseModel):
    product_id: str
    quantity: int
    user_id: str

@app.get("/catalog/{product_id}")
async def get_product(product_id: str):
    """Proxy request to catalog service"""
    logger.info(f"Proxying catalog request for product {product_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CATALOG_SERVICE_URL}/catalog/{product_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Catalog service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="Catalog service error")
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to catalog service: {e}")
        raise HTTPException(status_code=503, detail="Catalog service unavailable")

@app.get("/catalog")
async def list_products():
    """Proxy request to catalog service for product list"""
    logger.info("Proxying catalog list request")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CATALOG_SERVICE_URL}/catalog")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Catalog service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="Catalog service error")
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to catalog service: {e}")
        raise HTTPException(status_code=503, detail="Catalog service unavailable")

@app.post("/cart/add")
async def add_to_cart(item: CartItem):
    """Proxy request to cart service"""
    logger.info(f"Proxying cart add request: {item}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{CART_SERVICE_URL}/cart/add", json=item.dict())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Cart service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="Cart service error")
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to cart service: {e}")
        raise HTTPException(status_code=503, detail="Cart service unavailable")

@app.get("/cart/{cart_id}")
async def get_cart(cart_id: str):
    """Proxy request to cart service"""
    logger.info(f"Proxying cart get request for {cart_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CART_SERVICE_URL}/cart/{cart_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Cart service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="Cart service error")
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to cart service: {e}")
        raise HTTPException(status_code=503, detail="Cart service unavailable")

@app.delete("/cart/{cart_id}")
async def clear_cart(cart_id: str):
    """Proxy request to cart service"""
    logger.info(f"Proxying cart clear request for {cart_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{CART_SERVICE_URL}/cart/{cart_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Cart service error: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="Cart service error")
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to cart service: {e}")
        raise HTTPException(status_code=503, detail="Cart service unavailable")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "API Gateway",
        "version": "1.0.0",
        "catalog_service": CATALOG_SERVICE_URL,
        "cart_service": CART_SERVICE_URL,
        "endpoints": {
            "catalog": "/catalog/{product_id}",
            "cart_add": "/cart/add",
            "cart_get": "/cart/{cart_id}",
            "cart_clear": "/cart/{cart_id}",
            "health": "/healthz",
            "metrics": "/metrics"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
