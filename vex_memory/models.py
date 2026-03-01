"""
Pydantic models for vex-memory SDK.

Provides type-safe data models for Memory, Namespace, and other API entities.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class MemoryType(str, Enum):
    """Memory classification types."""
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    EMOTIONAL = "emotional"


class Memory(BaseModel):
    """Represents a memory object.
    
    Attributes:
        id: Unique memory identifier (assigned by server)
        type: Memory classification type
        content: The actual memory content
        importance_score: How important this memory is (0.0-1.0)
        confidence_score: Confidence in this memory (0.0-1.0)
        decay_factor: Rate at which memory decays over time
        access_count: Number of times memory has been accessed
        source: Optional source attribution
        event_time: When the remembered event occurred
        created_at: When memory was created
        namespace_id: Namespace this memory belongs to
        metadata: Additional structured data
    """
    
    id: Optional[str] = None
    type: MemoryType = MemoryType.SEMANTIC
    content: str
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    decay_factor: float = 1.0
    access_count: int = 0
    source: Optional[str] = None
    event_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    namespace_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class Namespace(BaseModel):
    """Represents a namespace for organizing memories.
    
    Attributes:
        namespace_id: Unique namespace identifier
        name: Human-readable namespace name
        owner_agent: Agent/user that owns this namespace
        access_policy: Access control rules (permissions by agent)
        created_at: When namespace was created
        updated_at: When namespace was last updated
    """
    
    namespace_id: str
    name: str
    owner_agent: str
    access_policy: Dict[str, List[str]] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None


class QueryResult(BaseModel):
    """Result from a semantic search query.
    
    Attributes:
        memories: List of matching memories
        total: Total number of matches
        query: Original query string
        max_tokens: Token limit that was applied
        tokens_used: Estimated tokens used in results
    """
    
    memories: List[Memory]
    total: int
    query: str
    max_tokens: Optional[int] = None
    tokens_used: Optional[int] = None


class ContextResult(BaseModel):
    """Formatted context for LLM prompts.
    
    Attributes:
        text: Formatted context text ready for LLM
        sources: Memory IDs that contributed to context
        token_count: Estimated token count
        truncated: Whether context was truncated to fit token limit
    """
    
    text: str
    sources: List[str]
    token_count: int
    truncated: bool = False


class SessionMessage(BaseModel):
    """A message in a conversation session.
    
    Attributes:
        role: Message role (user, assistant, system)
        content: Message content
        timestamp: When message was sent
        metadata: Optional additional data
    """
    
    role: str
    content: str
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is one of allowed values."""
        allowed = {"user", "assistant", "system"}
        if v not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v


class Session(BaseModel):
    """Represents a conversation session.
    
    Attributes:
        session_id: Unique session identifier
        messages: List of messages in this session
        created_at: When session was created
        updated_at: When session was last updated
        metadata: Optional additional data
    """
    
    session_id: str
    messages: List[SessionMessage] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    """Server health status.
    
    Attributes:
        status: Health status (healthy, ok, degraded, unhealthy)
        database: Database connection status
        memory_count: Total number of memories
        details: Optional detailed status information
    """
    
    status: str
    database: Optional[bool] = None
    memory_count: Optional[int] = None
    version: Optional[str] = None
    uptime_seconds: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class Stats(BaseModel):
    """Server statistics.
    
    Attributes:
        total_memories: Total number of memories
        total_entities: Total number of entities
        total_namespaces: Total number of namespaces (optional)
        total_sessions: Total number of sessions (optional)
        memory_types: Breakdown by memory type
        entity_types: Breakdown by entity type
        namespace_stats: Statistics per namespace (optional)
    """
    
    total_memories: int
    total_entities: Optional[int] = None
    total_namespaces: Optional[int] = None
    total_sessions: Optional[int] = None
    memory_types: Dict[str, int] = Field(default_factory=dict)
    entity_types: Dict[str, int] = Field(default_factory=dict)
    namespace_stats: Dict[str, Any] = Field(default_factory=dict)
