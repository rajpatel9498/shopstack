import os
import random
import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Add parent directory to path to import common module
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.observability import add_observability_routes, setup_otel_instrumentation

# Setup logging
logger = logging.getLogger(__name__)

# Setup OpenTelemetry if configured
setup_otel_instrumentation()

app = FastAPI(title="Cart Service", version="1.0.0")

# Add observability routes
add_observability_routes(app)

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    user_id: str

class CartResponse(BaseModel):
    message: str
    cart_id: str

# Simulate cart storage
cart_counter = 0
carts = {}

@app.post("/cart/add")
async def add_to_cart(item: CartItem):
    """Add item to cart with simulated write latency and 1% failure rate"""
    global cart_counter
    
    logger.info(f"Adding item to cart: {item.product_id} x{item.quantity} for user {item.user_id}")
    
    # Simulate database write latency (30-90ms)
    latency = random.uniform(0.03, 0.09)
    time.sleep(latency)
    
    # Simulate 1% failure rate
    if random.random() < 0.01:
        logger.error(f"Simulated failure for cart operation: {item}")
        raise HTTPException(status_code=500, detail="Internal server error - simulated failure")
    
    # Generate cart ID
    cart_counter += 1
    cart_id = f"cart_{cart_counter}"
    
    # Store cart item
    if cart_id not in carts:
        carts[cart_id] = []
    
    carts[cart_id].append(item)
    
    logger.info(f"Successfully added item to cart {cart_id}")
    
    return CartResponse(
        message="Item added to cart successfully",
        cart_id=cart_id
    )

@app.get("/cart/{cart_id}")
async def get_cart(cart_id: str):
    """Get cart contents"""
    logger.info(f"Fetching cart {cart_id}")
    
    if cart_id not in carts:
        logger.warning(f"Cart {cart_id} not found")
        raise HTTPException(status_code=404, detail="Cart not found")
    
    return {"cart_id": cart_id, "items": carts[cart_id]}

@app.delete("/cart/{cart_id}")
async def clear_cart(cart_id: str):
    """Clear cart contents"""
    logger.info(f"Clearing cart {cart_id}")
    
    if cart_id not in carts:
        logger.warning(f"Cart {cart_id} not found")
        raise HTTPException(status_code=404, detail="Cart not found")
    
    carts[cart_id] = []
    return {"message": "Cart cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
