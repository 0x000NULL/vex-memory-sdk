"""
Resilience patterns: retry logic and circuit breaker.

Provides automatic retries with exponential backoff and circuit breaker
pattern to prevent cascading failures.
"""

import time
from typing import Callable, Any, Optional
from enum import Enum
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import requests

from .exceptions import CircuitBreakerOpen, ServerError, TimeoutError, ConnectionError


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Too many failures, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Simple circuit breaker implementation.
    
    Tracks failures and opens the circuit when threshold is exceeded.
    After recovery timeout, enters half-open state to test recovery.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before entering half-open state
        success_threshold: Successes needed in half-open to close circuit
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Positional arguments to pass to func
            **kwargs: Keyword arguments to pass to func
        
        Returns:
            Result from func
        
        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        # Check if we should transition from open to half-open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitBreakerOpen(
                    f"Circuit breaker is open. "
                    f"Will retry in {self._time_until_retry():.0f}s"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to try recovery."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _time_until_retry(self) -> float:
        """Calculate seconds until retry is allowed."""
        if self.last_failure_time is None:
            return 0
        elapsed = time.time() - self.last_failure_time
        return max(0, self.recovery_timeout - elapsed)
    
    def _on_success(self):
        """Handle successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                # Recovered! Close the circuit
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        """Handle failed request."""
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery, open again
            self.state = CircuitState.OPEN
            self.failure_count = self.failure_threshold
        else:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN


def with_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
):
    """Decorator for automatic retry with exponential backoff.
    
    Retries on network errors, timeouts, and server errors (5xx).
    Does NOT retry on client errors (4xx) as those won't succeed.
    
    Args:
        max_attempts: Maximum number of attempts (including first try)
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
    
    Returns:
        Decorator function
    
    Example:
        @with_retry(max_attempts=3)
        def fetch_data():
            return requests.get("https://api.example.com/data")
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            ServerError,
            TimeoutError,
            ConnectionError,
        )),
        reraise=True,
    )
