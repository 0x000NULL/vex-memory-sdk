"""
Custom exceptions for vex-memory SDK.

Provides a clear exception hierarchy for different error conditions.
"""


class VexMemoryError(Exception):
    """Base exception for vex-memory SDK.
    
    All SDK-specific exceptions inherit from this class.
    """
    pass


class ConnectionError(VexMemoryError):
    """Failed to connect to vex-memory server.
    
    Raised when the HTTP client cannot reach the server.
    """
    pass


class AuthenticationError(VexMemoryError):
    """Authentication failed.
    
    Raised when API key is invalid or missing.
    """
    pass


class NotFoundError(VexMemoryError):
    """Resource not found (404).
    
    Raised when a requested memory, namespace, or session doesn't exist.
    """
    pass


class ValidationError(VexMemoryError):
    """Request validation failed.
    
    Raised when request parameters are invalid.
    """
    pass


class CircuitBreakerOpen(VexMemoryError):
    """Circuit breaker is open, requests blocked.
    
    Raised when too many failures have occurred and the circuit breaker
    has opened to prevent cascading failures.
    """
    pass


class RateLimitError(VexMemoryError):
    """Rate limit exceeded.
    
    Raised when API rate limit has been exceeded.
    """
    pass


class ServerError(VexMemoryError):
    """Server returned an error (5xx).
    
    Raised when the vex-memory server experiences an internal error.
    """
    pass


class TimeoutError(VexMemoryError):
    """Request timed out.
    
    Raised when a request takes longer than the configured timeout.
    """
    pass
