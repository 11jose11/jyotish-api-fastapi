"""Circuit breaker middleware for external service protection."""

import time
from enum import Enum
from typing import Dict, Callable, Any

from app.config import settings
from app.util.logging import get_logger

logger = get_logger("circuit_breaker")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker implementation."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 30,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker transitioning to CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            logger.warning(f"Circuit breaker transitioning to OPEN after {self.failure_count} failures")
            self.state = CircuitState.OPEN


# Global circuit breakers for different services
circuit_breakers = {
    "google_places": CircuitBreaker(failure_threshold=3, timeout=60),
    "swiss_ephemeris": CircuitBreaker(failure_threshold=5, timeout=30),
    "timezone": CircuitBreaker(failure_threshold=3, timeout=60)
}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get circuit breaker for service."""
    return circuit_breakers.get(service_name, CircuitBreaker())
