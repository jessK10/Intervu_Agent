"""
Observability Infrastructure for InterVu

Provides structured logging with structlog and distributed tracing
with OpenTelemetry for monitoring agent behavior and performance.
"""

import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    BatchSpanProcessor
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
import os
from typing import Optional


# Configure resource attributes
resource = Resource(attributes={
    ResourceAttributes.SERVICE_NAME: "intervu-backend",
    ResourceAttributes.SERVICE_VERSION: "1.0.0",
    "environment": os.getenv("APP_ENV", "development")
})

# Setup OpenTelemetry Tracer
tracer_provider = TracerProvider(resource=resource)

# Add span processor (console export for now, can add OTLP later)
tracer_provider.add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

# Set global tracer provider
trace.set_tracer_provider(tracer_provider)

# Get tracer for this application
tracer = trace.get_tracer("intervu.agents", "1.0.0")


# Configure structlog for structured JSON logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Get logger
logger = structlog.get_logger()


def log_agent_call(agent_name: str, input_data: dict, user_id: Optional[str] = None):
    """
    Log agent invocation with context.
    
    Args:
        agent_name: Name of the agent being called
        input_data: Input provided to the agent
        user_id: Optional user ID for tracking
    """
    logger.info(
        "agent_call_started",
        agent=agent_name,
        input_keys=list(input_data.keys()),
        user_id=user_id
    )


def log_agent_response(agent_name: str, success: bool, duration_ms: float, error: Optional[str] = None):
    """
    Log agent response with metrics.
    
    Args:
        agent_name: Name of the agent
        success: Whether call succeeded
        duration_ms: Execution time in milliseconds
        error: Optional error message
    """
    logger.info(
        "agent_call_completed",
        agent=agent_name,
        success=success,
        duration_ms=duration_ms,
        error=error
    )


def create_span(name: str, attributes: Optional[dict] = None):
    """
    Create a new tracing span with optional attributes.
    
    Args:
        name: Span name
        attributes: Key-value attributes for the span
        
    Returns:
        OpenTelemetry Span context manager
    """
    span = tracer.start_as_current_span(name)
    
    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, str(value))
    
    return span


# Export commonly used components
__all__ = [
    "logger",
    "tracer",
    "log_agent_call",
    "log_agent_response",
    "create_span"
]
