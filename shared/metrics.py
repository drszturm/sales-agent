import asyncio
import time
from functools import wraps

from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# Metrics
CALL_COUNTER = Counter("function_calls_total", "Total function calls", ["function"])
DURATION_HISTOGRAM = Histogram(
    "function_duration_seconds", "Function duration seconds", ["function"]
)


def instrument(func):
    """Decorator to instrument sync and async functions.

    Tracks call count and execution duration (seconds) per function name.
    """

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            CALL_COUNTER.labels(function=func.__name__).inc()
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                DURATION_HISTOGRAM.labels(function=func.__name__).observe(elapsed)

        return async_wrapper

    @wraps(func)
    def wrapper(*args, **kwargs):
        CALL_COUNTER.labels(function=func.__name__).inc()
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            DURATION_HISTOGRAM.labels(function=func.__name__).observe(elapsed)

    return wrapper


def metrics_endpoint():
    """Wsgi style metrics endpoint for FastAPI registrations."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


__all__ = ["instrument", "metrics_endpoint"]
