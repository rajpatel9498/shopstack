import os
import logging
import time
from typing import Optional, Callable
from functools import wraps

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Prometheus metrics
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "%(name)s"}'
)

logger = logging.getLogger(__name__)

def setup_otel_instrumentation():
    """Setup OpenTelemetry instrumentation if OTLP endpoint is configured"""
    otlp_endpoint = os.getenv('OTLP_ENDPOINT')
    if otlp_endpoint:
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            
            # Setup trace provider
            trace.set_tracer_provider(TracerProvider())
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
            )
            
            logger.info(f"OpenTelemetry instrumentation enabled with OTLP endpoint: {otlp_endpoint}")
        except ImportError:
            logger.warning("OpenTelemetry packages not installed. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp")
        except Exception as e:
            logger.error(f"Failed to setup OpenTelemetry: {e}")

class MetricsMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for collecting Prometheus metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Get trace context if available
        trace_id = None
        span_id = None
        try:
            from opentelemetry import trace
            current_span = trace.get_current_span()
            if current_span:
                trace_id = current_span.get_span_context().trace_id
                span_id = current_span.get_span_context().span_id
        except ImportError:
            pass
        
        # Log request with trace context
        logger.info(
            f"Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "trace_id": trace_id,
                "span_id": span_id
            }
        )
        
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        endpoint = request.url.path
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
        
        # Log response with trace context
        logger.info(
            f"Request completed",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration": duration,
                "trace_id": trace_id,
                "span_id": span_id
            }
        )
        
        return response

def get_metrics():
    """Return Prometheus metrics"""
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

def add_observability_routes(app):
    """Add observability endpoints to FastAPI app"""
    app.add_middleware(MetricsMiddleware)
    
    @app.get("/metrics")
    async def metrics():
        return get_metrics()
    
    @app.get("/healthz")
    async def healthz():
        return {"status": "healthy"}
    
    @app.get("/livez")
    async def livez():
        return {"status": "alive"}
