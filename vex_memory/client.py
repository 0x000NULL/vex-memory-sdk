"""
Main MemoryClient class for vex-memory SDK.

Provides simple, resource-based, and expert-level APIs for interacting
with the vex-memory server.
"""

import requests
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import os

from .models import (
    Memory,
    Namespace,
    Session,
    SessionMessage,
    HealthStatus,
    Stats,
    MemoryType,
)
from .exceptions import (
    VexMemoryError,
    ConnectionError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError,
    TimeoutError,
    RateLimitError,
)
from .resilience import CircuitBreaker, with_retry
from .resources import MemoryResource, QueryResource, NamespaceResource, SessionResource


class MemoryClient:
    """
    vex-memory Python SDK client.
    
    Three usage patterns:
    1. Simple API: client.store(), client.search()
    2. Resource-based API: client.memories.create()
    3. Expert API: Full config with circuit breaker, retry, etc.
    
    Examples:
        Simple usage:
        >>> client = MemoryClient("http://localhost:8000")
        >>> memory = client.store("Meeting notes")
        >>> results = client.search("what meetings?")
        
        Resource-based:
        >>> memory = client.memories.create(content="Fact", importance=0.9)
        >>> client.namespaces.grant_access("ns-id", "agent-id", ["read"])
        
        Context manager:
        >>> with MemoryClient() as client:
        ...     memory = client.store("Note")
    
    Args:
        base_url: vex-memory server URL (default: http://localhost:8000)
        timeout: Request timeout in seconds (default: 30)
        enable_circuit_breaker: Enable circuit breaker pattern (default: False)
        retry_attempts: Maximum retry attempts (default: 3)
        api_key: Optional API key for authentication
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        enable_circuit_breaker: bool = False,
        retry_attempts: int = 3,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        
        # Initialize requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'vex-memory-python/1.0.0',
            'Content-Type': 'application/json',
        })
        
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
        
        # Circuit breaker (optional)
        self.circuit_breaker = CircuitBreaker() if enable_circuit_breaker else None
        
        # Current namespace
        self._current_namespace: Optional[str] = None
        
        # Resource abstractions (advanced usage)
        self.memories = MemoryResource(self)
        self.namespaces = NamespaceResource(self)
        self.queries = QueryResource(self)
        self.sessions = SessionResource(self)
    
    @classmethod
    def from_env(cls) -> "MemoryClient":
        """Create client from environment variables.
        
        Reads configuration from:
        - VEX_MEMORY_URL: Server URL
        - VEX_MEMORY_API_KEY: API key
        - VEX_MEMORY_TIMEOUT: Request timeout
        - VEX_MEMORY_MAX_RETRIES: Maximum retries
        
        Returns:
            Configured MemoryClient instance
        """
        return cls(
            base_url=os.getenv("VEX_MEMORY_URL", "http://localhost:8000"),
            api_key=os.getenv("VEX_MEMORY_API_KEY"),
            timeout=int(os.getenv("VEX_MEMORY_TIMEOUT", "30")),
            retry_attempts=int(os.getenv("VEX_MEMORY_MAX_RETRIES", "3")),
        )
    
    # === CONTEXT MANAGER SUPPORT ===
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and cleanup."""
        self.close()
    
    def close(self):
        """Close HTTP session and cleanup resources."""
        self.session.close()
    
    # === SIMPLE API (Beginner-Friendly) ===
    
    def store(
        self,
        content: str,
        type: str = "semantic",
        importance: float = 0.5,
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        **kwargs
    ) -> Memory:
        """Store a memory (simple API).
        
        Args:
            content: Memory content
            type: Memory type (semantic, episodic, procedural, emotional)
            importance: Importance score (0.0-1.0)
            confidence: Confidence score (0.0-1.0)
            metadata: Optional structured metadata
            source: Optional source attribution
            **kwargs: Additional fields
        
        Returns:
            Created Memory object
        
        Examples:
            >>> client = MemoryClient()
            >>> memory = client.store("Python 3.12 released")
            >>> memory = client.store(
            ...     "Meeting with team",
            ...     importance=0.8,
            ...     metadata={"attendees": ["Alice", "Bob"]}
            ... )
        """
        payload = {
            "content": content,
            "type": type,
            "importance_score": importance,
            "confidence_score": confidence,
            "metadata": metadata or {},
            **kwargs
        }
        
        if source:
            payload["source"] = source
        
        if self._current_namespace:
            payload["namespace_id"] = self._current_namespace
        
        response = self._request("POST", "/memories", json=payload)
        return Memory(**response)
    
    def get(self, memory_id: str) -> Memory:
        """Retrieve a memory by ID.
        
        Args:
            memory_id: Memory identifier
        
        Returns:
            Memory object
        
        Raises:
            NotFoundError: If memory doesn't exist
        """
        response = self._request("GET", f"/memories/{memory_id}")
        return Memory(**response)
    
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        importance: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Memory:
        """Update an existing memory.
        
        Args:
            memory_id: Memory identifier
            content: New content (if updating)
            importance: New importance score (if updating)
            metadata: New metadata (if updating)
            **kwargs: Additional fields to update
        
        Returns:
            Updated Memory object
        """
        payload = {}
        
        if content is not None:
            payload["content"] = content
        if importance is not None:
            payload["importance_score"] = importance
        if metadata is not None:
            payload["metadata"] = metadata
        
        payload.update(kwargs)
        
        response = self._request("PUT", f"/memories/{memory_id}", json=payload)
        return Memory(**response)
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory.
        
        Args:
            memory_id: Memory identifier
        
        Returns:
            True if deleted successfully
        """
        self._request("DELETE", f"/memories/{memory_id}")
        return True
    
    def store_many(
        self,
        memories: List[Union[str, Dict[str, Any]]]
    ) -> List[Memory]:
        """Store multiple memories at once (bulk operation).
        
        Args:
            memories: List of memory contents (strings) or dicts with full data
        
        Returns:
            List of created Memory objects
        
        Examples:
            >>> memories = client.store_many([
            ...     "Quick note 1",
            ...     "Quick note 2",
            ...     {"content": "Detailed", "importance": 0.9},
            ... ])
        """
        # Normalize to list of dicts
        normalized = []
        for item in memories:
            if isinstance(item, str):
                normalized.append({"content": item})
            else:
                normalized.append(item)
        
        # Add current namespace if set
        if self._current_namespace:
            for item in normalized:
                if "namespace_id" not in item:
                    item["namespace_id"] = self._current_namespace
        
        response = self._request("POST", "/memories/bulk", json={"memories": normalized})
        
        # Handle response format - bulk endpoint returns {created, failed, ids}
        if "ids" in response:
            # Fetch the created memories
            memories = []
            for memory_id in response.get("ids", []):
                try:
                    memory = self.get(memory_id)
                    memories.append(memory)
                except:
                    # If we can't fetch, create minimal Memory object
                    pass
            return memories
        elif "memories" in response:
            # Alternative format (if API returns full objects)
            return [Memory(**m) for m in response["memories"]]
        else:
            return []
    
    def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        min_score: Optional[float] = None,
        namespace: Optional[str] = None,
        **filters
    ) -> List[Memory]:
        """Search memories (simple API).
        
        Args:
            query: Search query
            limit: Maximum results
            offset: Number of results to skip
            min_score: Minimum similarity score threshold
            namespace: Optional namespace filter
            **filters: Additional filters
        
        Returns:
            List of matching Memory objects with similarity scores
        
        Examples:
            >>> results = client.search("what meetings?")
            >>> results = client.search(
            ...     "project updates",
            ...     limit=20,
            ...     min_score=0.7,
            ... )
        """
        payload = {
            "query": query,
            "limit": limit,
            "offset": offset,
            **filters
        }
        
        if min_score is not None:
            payload["min_score"] = min_score
        
        if namespace:
            payload["namespace"] = namespace
        elif self._current_namespace:
            payload["namespace"] = self._current_namespace
        
        response = self._request("POST", "/query", json=payload)
        
        # Handle different response formats
        if isinstance(response, dict) and "memories" in response:
            memories_data = response["memories"]
        else:
            memories_data = response
        
        return [Memory(**m) for m in memories_data]
    
    def find_one(self, query: str, **filters) -> Optional[Memory]:
        """Find single best match.
        
        Args:
            query: Search query
            **filters: Additional filters
        
        Returns:
            Best matching Memory or None
        """
        results = self.search(query=query, limit=1, **filters)
        return results[0] if results else None
    
    def build_context(
        self,
        query: str,
        max_tokens: int = 4000,
        include_metadata: bool = False,
        **filters
    ) -> str:
        """Build formatted context for LLM prompts.
        
        Args:
            query: Context query
            max_tokens: Maximum tokens to use
            include_metadata: Include memory metadata in context
            **filters: Additional filters
        
        Returns:
            Formatted context text ready for LLM
        
        Examples:
            >>> context = client.build_context("project status")
            >>> response = llm.complete(context + "\\n\\nWhat's the status?")
        """
        # Search for relevant memories
        memories = self.search(query=query, limit=20, **filters)
        
        if not memories:
            return ""
        
        # Format for LLM
        lines = ["# Relevant Context\n"]
        
        for i, memory in enumerate(memories, 1):
            lines.append(f"## Memory {i}")
            lines.append(f"Content: {memory.content}")
            
            if include_metadata and memory.metadata:
                lines.append(f"Metadata: {memory.metadata}")
            
            lines.append("")  # Blank line
        
        context = "\n".join(lines)
        
        # Simple token estimation (rough: 1 token ≈ 4 chars)
        estimated_tokens = len(context) // 4
        
        # Truncate if needed (simple: just cut at token limit)
        if estimated_tokens > max_tokens:
            max_chars = max_tokens * 4
            context = context[:max_chars] + "\n\n[Context truncated...]"
        
        return context
    
    # === SESSION MANAGEMENT ===
    
    def create_session(
        self,
        session_id: str,
        **metadata
    ) -> Session:
        """Create a conversation session.
        
        Args:
            session_id: Unique session identifier
            **metadata: Optional metadata
        
        Returns:
            Created Session object
        """
        payload = {
            "session_id": session_id,
            "metadata": metadata
        }
        
        response = self._request("POST", "/sessions", json=payload)
        return Session(**response)
    
    def get_session(self, session_id: str) -> Session:
        """Get session details.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session object
        """
        response = self._request("GET", f"/sessions/{session_id}")
        return Session(**response)
    
    def add_to_session(
        self,
        session_id: str,
        role: str,
        content: str,
        **metadata
    ) -> Session:
        """Add a message to session.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message content
            **metadata: Optional metadata
        
        Returns:
            Updated Session object
        """
        payload = {
            "role": role,
            "content": content,
            "metadata": metadata
        }
        
        response = self._request("POST", f"/sessions/{session_id}/messages", json=payload)
        return Session(**response)
    
    def get_session_context(
        self,
        session_id: str,
        max_tokens: int = 4000
    ) -> str:
        """Get formatted context from session.
        
        Args:
            session_id: Session identifier
            max_tokens: Maximum tokens to use
        
        Returns:
            Formatted context text
        """
        session = self.get_session(session_id)
        
        # Format messages for LLM
        lines = []
        for msg in session.messages:
            lines.append(f"{msg.role}: {msg.content}")
        
        context = "\n".join(lines)
        
        # Truncate if needed
        estimated_tokens = len(context) // 4
        if estimated_tokens > max_tokens:
            max_chars = max_tokens * 4
            context = context[:max_chars] + "\n[Session truncated...]"
        
        return context
    
    # === NAMESPACE OPERATIONS ===
    
    def create_namespace(
        self,
        name: str,
        owner: str,
        description: Optional[str] = None
    ) -> Namespace:
        """Create a new namespace.
        
        Args:
            name: Namespace name
            owner: Owner agent ID
            description: Optional description
        
        Returns:
            Created Namespace object
        """
        payload = {
            "name": name,
            "owner_agent": owner,
        }
        
        if description:
            payload["description"] = description
        
        response = self._request("POST", "/namespaces", json=payload)
        return Namespace(**response)
    
    def list_namespaces(self) -> List[Namespace]:
        """List all accessible namespaces.
        
        Returns:
            List of Namespace objects
        """
        response = self._request("GET", "/namespaces")
        
        if isinstance(response, dict) and "namespaces" in response:
            namespaces_data = response["namespaces"]
        else:
            namespaces_data = response
        
        return [Namespace(**ns) for ns in namespaces_data]
    
    def get_namespace(self, namespace_id: str) -> Namespace:
        """Get namespace details.
        
        Args:
            namespace_id: Namespace identifier
        
        Returns:
            Namespace object
        """
        response = self._request("GET", f"/namespaces/{namespace_id}")
        return Namespace(**response)
    
    def use_namespace(self, namespace_id: str):
        """Switch to a different namespace.
        
        All subsequent operations will use this namespace.
        
        Args:
            namespace_id: Namespace identifier to switch to
        """
        self._current_namespace = namespace_id
    
    def namespace(self, namespace_id: str):
        """Context manager for temporary namespace switch.
        
        Args:
            namespace_id: Namespace to use temporarily
        
        Examples:
            >>> with client.namespace("work"):
            ...     work_memories = client.search("meetings")
            # Auto-switches back after context
        """
        return NamespaceContext(self, namespace_id)
    
    def grant_namespace_access(
        self,
        namespace_id: str,
        agent_id: str,
        permissions: List[str]
    ) -> bool:
        """Grant access to a namespace.
        
        Args:
            namespace_id: Namespace identifier
            agent_id: Agent to grant access to
            permissions: List of permissions (e.g., ["read", "write"])
        
        Returns:
            True if successful
        """
        payload = {
            "agent_id": agent_id,
            "permissions": permissions
        }
        
        self._request("POST", f"/namespaces/{namespace_id}/grant", json=payload)
        return True
    
    # === ADMIN / MONITORING ===
    
    def health(self) -> HealthStatus:
        """Check server health status.
        
        Returns:
            HealthStatus object with server health info
        """
        response = self._request("GET", "/health")
        return HealthStatus(**response)
    
    def stats(self) -> Stats:
        """Get server statistics.
        
        Returns:
            Stats object with usage statistics
        """
        response = self._request("GET", "/stats")
        return Stats(**response)
    
    # === INTERNAL REQUEST METHOD ===
    
    @with_retry(max_attempts=3)
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Any:
        """Internal method to make HTTP requests with retry and circuit breaker.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (with leading slash)
            **kwargs: Additional arguments for requests
        
        Returns:
            Response JSON data
        
        Raises:
            ConnectionError: If cannot connect to server
            AuthenticationError: If authentication fails
            NotFoundError: If resource not found
            ValidationError: If request validation fails
            ServerError: If server returns 5xx error
            TimeoutError: If request times out
        """
        url = f"{self.base_url}{endpoint}"
        
        # Set timeout if not specified
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        # Wrap in circuit breaker if enabled
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                self._do_request,
                method,
                url,
                **kwargs
            )
        else:
            return self._do_request(method, url, **kwargs)
    
    def _do_request(self, method: str, url: str, **kwargs) -> Any:
        """Actually perform the HTTP request.
        
        Args:
            method: HTTP method
            url: Full URL
            **kwargs: Request arguments
        
        Returns:
            Response JSON data
        """
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            elif response.status_code == 404:
                raise NotFoundError(f"Resource not found: {url}")
            elif response.status_code == 422:
                raise ValidationError(f"Validation error: {response.text}")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif 500 <= response.status_code < 600:
                raise ServerError(f"Server error ({response.status_code}): {response.text}")
            
            response.raise_for_status()
            
            # Return JSON if available
            if response.content:
                return response.json()
            else:
                return {}
        
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {url}: {e}")
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timed out: {e}")
        except requests.exceptions.RequestException as e:
            raise VexMemoryError(f"Request failed: {e}")


class NamespaceContext:
    """Context manager for temporary namespace switching."""
    
    def __init__(self, client: MemoryClient, namespace_id: str):
        self.client = client
        self.namespace_id = namespace_id
        self.previous_namespace = None
    
    def __enter__(self):
        """Save current namespace and switch to new one."""
        self.previous_namespace = self.client._current_namespace
        self.client._current_namespace = self.namespace_id
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore previous namespace."""
        self.client._current_namespace = self.previous_namespace
