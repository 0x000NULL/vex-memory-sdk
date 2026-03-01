"""
Resource abstractions for advanced API usage.

Provides resource-based API (client.memories.create()) for power users
who prefer organized, IDE-friendly method grouping.
"""

from typing import List, Dict, Any, Optional, Iterator
from .models import Memory, Namespace, Session, SessionMessage, QueryResult


class MemoryResource:
    """Advanced memory operations.
    
    Provides CRUD operations and bulk operations for memories.
    """
    
    def __init__(self, client):
        """Initialize resource with client reference.
        
        Args:
            client: MemoryClient instance
        """
        self.client = client
    
    def create(
        self,
        content: str,
        type: str = "semantic",
        importance: float = 0.5,
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Memory:
        """Create a new memory.
        
        Args:
            content: Memory content
            type: Memory type (semantic, episodic, procedural, emotional)
            importance: Importance score (0.0-1.0)
            confidence: Confidence score (0.0-1.0)
            metadata: Optional structured metadata
            **kwargs: Additional fields
        
        Returns:
            Created Memory object
        """
        return self.client.store(
            content=content,
            type=type,
            importance=importance,
            confidence=confidence,
            metadata=metadata,
            **kwargs
        )
    
    def get(self, memory_id: str) -> Memory:
        """Retrieve a memory by ID.
        
        Args:
            memory_id: Memory identifier
        
        Returns:
            Memory object
        """
        return self.client.get(memory_id)
    
    def list(
        self,
        limit: int = 10,
        offset: int = 0,
        namespace: Optional[str] = None,
        **filters
    ) -> List[Memory]:
        """List memories with optional filters.
        
        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            namespace: Optional namespace filter
            **filters: Additional filter criteria
        
        Returns:
            List of Memory objects
        """
        # This would call a list endpoint
        # For now, we'll implement as search with empty query
        return self.client.search(
            query="",
            limit=limit,
            offset=offset,
            namespace=namespace,
            **filters
        )
    
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
        return self.client.update(
            memory_id=memory_id,
            content=content,
            importance=importance,
            metadata=metadata,
            **kwargs
        )
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory.
        
        Args:
            memory_id: Memory identifier
        
        Returns:
            True if deleted successfully
        """
        return self.client.delete(memory_id)
    
    def bulk_create(self, memories: List[Dict[str, Any]]) -> List[Memory]:
        """Create multiple memories at once.
        
        Args:
            memories: List of memory data dictionaries
        
        Returns:
            List of created Memory objects
        """
        return self.client.store_many(memories)
    
    def stream(
        self,
        chunk_size: int = 100,
        **filters
    ) -> Iterator[Memory]:
        """Stream large result sets.
        
        Args:
            chunk_size: Number of memories per batch
            **filters: Filter criteria
        
        Yields:
            Memory objects one at a time
        """
        offset = 0
        while True:
            batch = self.list(limit=chunk_size, offset=offset, **filters)
            if not batch:
                break
            
            for memory in batch:
                yield memory
            
            offset += chunk_size
            
            # Stop if we got fewer than chunk_size (last page)
            if len(batch) < chunk_size:
                break


class QueryResource:
    """Advanced query operations.
    
    Provides semantic search and context building.
    """
    
    def __init__(self, client):
        """Initialize resource with client reference.
        
        Args:
            client: MemoryClient instance
        """
        self.client = client
    
    def search(
        self,
        query: str,
        limit: int = 10,
        min_score: Optional[float] = None,
        **filters
    ) -> List[Memory]:
        """Semantic search for memories.
        
        Args:
            query: Search query
            limit: Maximum results
            min_score: Minimum similarity score threshold
            **filters: Additional filters
        
        Returns:
            List of matching Memory objects
        """
        return self.client.search(
            query=query,
            limit=limit,
            min_score=min_score,
            **filters
        )
    
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
        **filters
    ) -> str:
        """Build formatted context for LLM prompts.
        
        Args:
            query: Context query
            max_tokens: Maximum tokens to use
            **filters: Additional filters
        
        Returns:
            Formatted context text
        """
        return self.client.build_context(
            query=query,
            max_tokens=max_tokens,
            **filters
        )


class NamespaceResource:
    """Advanced namespace operations.
    
    Provides namespace management and access control.
    """
    
    def __init__(self, client):
        """Initialize resource with client reference.
        
        Args:
            client: MemoryClient instance
        """
        self.client = client
    
    def create(
        self,
        name: str,
        owner: str,
        description: Optional[str] = None,
    ) -> Namespace:
        """Create a new namespace.
        
        Args:
            name: Namespace name
            owner: Owner agent ID
            description: Optional description
        
        Returns:
            Created Namespace object
        """
        return self.client.create_namespace(
            name=name,
            owner=owner,
            description=description
        )
    
    def list(self) -> List[Namespace]:
        """List all accessible namespaces.
        
        Returns:
            List of Namespace objects
        """
        return self.client.list_namespaces()
    
    def get(self, namespace_id: str) -> Namespace:
        """Get namespace details.
        
        Args:
            namespace_id: Namespace identifier
        
        Returns:
            Namespace object
        """
        return self.client.get_namespace(namespace_id)
    
    def grant_access(
        self,
        namespace_id: str,
        agent_id: str,
        permissions: List[str],
    ) -> bool:
        """Grant access to a namespace.
        
        Args:
            namespace_id: Namespace identifier
            agent_id: Agent to grant access to
            permissions: List of permissions (e.g., ["read", "write"])
        
        Returns:
            True if successful
        """
        return self.client.grant_namespace_access(
            namespace_id=namespace_id,
            agent_id=agent_id,
            permissions=permissions
        )


class SessionResource:
    """Advanced session operations.
    
    Provides conversation session management.
    """
    
    def __init__(self, client):
        """Initialize resource with client reference.
        
        Args:
            client: MemoryClient instance
        """
        self.client = client
    
    def create(self, session_id: str, **metadata) -> Session:
        """Create a new session.
        
        Args:
            session_id: Unique session identifier
            **metadata: Optional metadata
        
        Returns:
            Created Session object
        """
        return self.client.create_session(session_id=session_id, **metadata)
    
    def get(self, session_id: str) -> Session:
        """Get session details.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session object
        """
        return self.client.get_session(session_id)
    
    def add_message(
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
        return self.client.add_to_session(
            session_id=session_id,
            role=role,
            content=content,
            **metadata
        )
    
    def get_context(
        self,
        session_id: str,
        max_tokens: int = 4000,
    ) -> str:
        """Get formatted context from session.
        
        Args:
            session_id: Session identifier
            max_tokens: Maximum tokens to use
        
        Returns:
            Formatted context text
        """
        return self.client.get_session_context(
            session_id=session_id,
            max_tokens=max_tokens
        )
