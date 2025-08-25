#!/bin/bash

echo "🚀 Starting load test to trigger autoscaling..."
echo "Target: http://localhost:8080"

# Generate load for 2 minutes
for i in {1..120}; do
    # Catalog browsing (70% of traffic)
    if [ $((i % 10)) -lt 7 ]; then
        curl -s "http://localhost:8080/catalog/$((RANDOM % 1000))" > /dev/null &
    else
        # Cart operations (30% of traffic)
        curl -s -X POST "http://localhost:8080/cart/add" \
            -H "Content-Type: application/json" \
            -d "{\"user_id\": \"user$((RANDOM % 100))\", \"product_id\": \"$((RANDOM % 1000))\", \"quantity\": $((RANDOM % 5 + 1))}" > /dev/null &
    fi
    
    # Health check
    curl -s "http://localhost:8080/healthz" > /dev/null &
    
    # Metrics endpoint
    curl -s "http://localhost:8080/metrics" > /dev/null &
    
    # Wait 1 second between requests
    sleep 1
    
    # Show progress every 10 seconds
    if [ $((i % 10)) -eq 0 ]; then
        echo "⏱️  Load test progress: $i/120 seconds"
        echo "📊 Current pod count:"
        kubectl get pods -n shopstack --no-headers | wc -l
    fi
done

echo "✅ Load test completed!"
echo "📊 Final pod count:"
kubectl get pods -n shopstack
