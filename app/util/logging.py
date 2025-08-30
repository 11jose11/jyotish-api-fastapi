"""JSON logging configuration for Jyotiṣa API."""

import json
import logging
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict

from app.config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, "route"):
            log_entry["route"] = record.route
        if hasattr(record, "latency_ms"):
            log_entry["latency_ms"] = record.latency_ms
        if hasattr(record, "status"):
            log_entry["status"] = record.status
        if hasattr(record, "req_id"):
            log_entry["req_id"] = record.req_id
        if hasattr(record, "error"):
            log_entry["error"] = record.error
            
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)


def setup_logging() -> None:
    """Setup JSON logging configuration."""
    # Create logger
    logger = logging.getLogger("jyotish")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # Set as root logger
    logging.getLogger().handlers = []
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().setLevel(getattr(logging, settings.log_level.upper()))


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(f"jyotish.{name}")


class RequestLogger:
    """Request logging context manager."""
    
    def __init__(self, route: str, req_id: str = None):
        self.route = route
        self.req_id = req_id or str(uuid.uuid4())
        self.start_time = time.time()
        self.logger = get_logger("request")
        
    def __enter__(self):
        self.logger.info(
            "Request started",
            extra={
                "route": self.route,
                "req_id": self.req_id,
                "status": "started"
            }
        )
        return self
        
    def success(self):
        """Mark request as successful."""
        latency_ms = int((time.time() - self.start_time) * 1000)
        self.logger.info(
            "Request completed successfully",
            extra={
                "route": self.route,
                "req_id": self.req_id,
                "latency_ms": latency_ms,
                "status": "success"
            }
        )
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = int((time.time() - self.start_time) * 1000)
        
        if exc_type:
            self.logger.error(
                "Request failed",
                extra={
                    "route": self.route,
                    "req_id": self.req_id,
                    "latency_ms": latency_ms,
                    "status": "error",
                    "error": str(exc_val)
                },
                exc_info=(exc_type, exc_val, exc_tb)
            )
        else:
            self.logger.info(
                "Request completed",
                extra={
                    "route": self.route,
                    "req_id": self.req_id,
                    "latency_ms": latency_ms,
                    "status": "success"
                }
            )
