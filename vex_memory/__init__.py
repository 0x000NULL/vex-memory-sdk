"""
vex-memory Python SDK

Official Python SDK for vex-memory - A human-inspired memory system for AI agents.

Simple usage:
    from vex_memory import MemoryClient
    
    client = MemoryClient("http://localhost:8000")
    client.store("Python 3.12 released", importance=0.8)
    results = client.search("what's new in Python?")

Advanced usage:
    client.memories.create(content="fact", confidence=0.9)
    client.namespaces.grant_access("ns-id", "agent", ["read"])

Context manager:
    with MemoryClient() as client:
        memory = client.store("Note")

Module-level shortcuts:
    from vex_memory import store, search
    
    store("Quick note")
    results = search("query")
"""

__version__ = "1.0.0"

from .client import MemoryClient
from .models import (
    Memory,
    Namespace,
    Session,
    SessionMessage,
    MemoryType,
    QueryResult,
    ContextResult,
    HealthStatus,
    Stats,
)
from .exceptions import (
    VexMemoryError,
    ConnectionError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    CircuitBreakerOpen,
    RateLimitError,
    ServerError,
    TimeoutError,
)

__all__ = [
    # Version
    "__version__",
    
    # Main client
    "MemoryClient",
    
    # Models
    "Memory",
    "Namespace",
    "Session",
    "SessionMessage",
    "MemoryType",
    "QueryResult",
    "ContextResult",
    "HealthStatus",
    "Stats",
    
    # Exceptions
    "VexMemoryError",
    "ConnectionError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "CircuitBreakerOpen",
    "RateLimitError",
    "ServerError",
    "TimeoutError",
    
    # Module-level shortcuts
    "store",
    "search",
    "find_one",
    "build_context",
]


# === MODULE-LEVEL SHORTCUTS ===
# For quick scripts, REPL, and Jupyter notebooks

_default_client = None


def _get_default_client() -> MemoryClient:
    """Get or create the default client instance.
    
    Returns:
        Shared MemoryClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = MemoryClient.from_env()
    return _default_client


def store(content: str, **kwargs) -> Memory:
    """Store a memory using default client.
    
    Args:
        content: Memory content
        **kwargs: Additional arguments for store()
    
    Returns:
        Created Memory object
    
    Examples:
        >>> from vex_memory import store
        >>> memory = store("Quick note")
    """
    return _get_default_client().store(content, **kwargs)


def search(query: str, **kwargs) -> list:
    """Search memories using default client.
    
    Args:
        query: Search query
        **kwargs: Additional arguments for search()
    
    Returns:
        List of matching Memory objects
    
    Examples:
        >>> from vex_memory import search
        >>> results = search("what meetings?")
    """
    return _get_default_client().search(query, **kwargs)


def find_one(query: str, **kwargs) -> Memory:
    """Find single best match using default client.
    
    Args:
        query: Search query
        **kwargs: Additional arguments
    
    Returns:
        Best matching Memory or None
    """
    return _get_default_client().find_one(query, **kwargs)


def build_context(query: str, **kwargs) -> str:
    """Build formatted context using default client.
    
    Args:
        query: Context query
        **kwargs: Additional arguments
    
    Returns:
        Formatted context text
    """
    return _get_default_client().build_context(query, **kwargs)
