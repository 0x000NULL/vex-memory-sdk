# Vex Memory SDK

Python client library for the vex-memory API with intelligent context building.

## Installation

```bash
pip install vex-memory-sdk
```

Or from source:
```bash
git clone https://github.com/0x000NULL/vex-memory-sdk
cd vex-memory-sdk
pip install -e .
```

## Quick Start

```python
from vex_memory import VexMemoryClient

# Initialize client
client = VexMemoryClient(base_url="http://localhost:8000")

# Store a memory
memory = client.store_memory(
    content="The project launch is scheduled for March 15th",
    importance_score=0.8,
    memory_type="event"
)

# Build intelligent context (v1.2.0 - now with MMR!)
context = client.build_context(
    query="When is the project launch?",
    token_budget=2000,
    model="gpt-4",
    use_mmr=True  # NEW: Use Maximal Marginal Relevance
)

print(f"Context uses {context['metadata']['total_tokens']} tokens")
print(f"Selected {len(context['memories'])} memories")

# Format for LLM
formatted = client.format_context_for_llm(context)
```

## Features

### Smart Context Building (v1.2.0)

The `build_context()` method uses intelligent prioritization with MMR support:

```python
context = client.build_context(
    query="What did we discuss about the database?",
    token_budget=4000,        # Maximum tokens to use
    model="gpt-4",            # LLM model for token counting
    weights={                 # Optional custom weights
        "similarity": 0.5,
        "importance": 0.3,
        "recency": 0.2,
        "diversity": 0.0
    },
    diversity_threshold=0.7,  # Jaccard similarity threshold
    min_score=0.5,            # Filter low-score memories
    namespace="my-namespace", # Optional namespace filter
    use_mmr=True,             # NEW v1.2.0: Use MMR for better diversity
    mmr_lambda=0.7            # NEW v1.2.0: Balance relevance (1.0) vs diversity (0.0)
)
```

Returns:
```python
{
    "memories": [
        {
            "id": "...",
            "content": "...",
            "importance_score": 0.85,
            "_score": 0.78,  # Composite score
            "_score_factors": {
                "similarity": 0.92,
                "importance": 0.85,
                "recency": 0.65
            }
        }
    ],
    "metadata": {
        "total_tokens": 3847,
        "budget": 4000,
        "utilization": 0.96,
        "memories_selected": 12,
        "diversity_filtered": 5,
        "average_score": 0.73
    }
}
```

### Weight Presets (v1.2.0)

Get optimized weight configurations for different use cases:

```python
# List available presets
presets = client.get_weight_presets()
for preset in presets['presets']:
    print(f"{preset['name']}: {preset['description']}")

# Get recommended weights for a specific use case
config = client.get_recommended_weights(use_case="entity_focused")
print(f"Using: {config['name']}")
print(f"Weights: {config['weights']}")

# Use preset weights in context building
context = client.build_context(
    query="project updates",
    token_budget=2000,
    weights=config['weights']  # Apply preset weights
)
```

Available presets:
- **balanced**: Balanced across all factors (default)
- **relevance_focused**: Prioritizes similarity and importance
- **recency_focused**: Prioritizes recent memories
- **diversity_focused**: Maximizes variety and coverage
- **entity_focused**: Prioritizes entity coverage
- **importance_focused**: Prioritizes memory importance

### Context Formatting

Format memories for your LLM:

```python
# Simple concatenation
formatted = client.format_context_for_llm(context)

# Custom formatting
formatted = client.format_context_for_llm(
    context,
    include_scores=True,  # Include score information
    include_timestamps=True,
    separator="\n\n---\n\n"
)
```

### Traditional Methods

All standard vex-memory operations are supported:

```python
# Store memory
memory = client.store_memory(
    content="User prefers dark mode",
    importance_score=0.7,
    memory_type="preference",
    metadata={"category": "ui"}
)

# Query memories (simple semantic search)
results = client.query_memories(
    query="dark mode preferences",
    limit=10
)

# Get memory by ID
memory = client.get_memory("memory-id-123")

# Update memory
client.update_memory(
    "memory-id-123",
    importance_score=0.9
)

# Delete memory
client.delete_memory("memory-id-123")

# Extract from text
extracted = client.extract_memories(
    "We decided to use PostgreSQL. The database will be hosted on AWS."
)

# Create namespace
namespace = client.create_namespace(
    name="project-alpha",
    description="Memories for Project Alpha"
)

# Grant access
client.grant_access(
    namespace_id=namespace["namespace_id"],
    agent_id="agent-123",
    permission="write"
)
```

## API Reference

### VexMemoryClient

```python
class VexMemoryClient:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """Initialize client.
        
        Args:
            base_url: Base URL of vex-memory API
            timeout: Request timeout in seconds
        """
    
    def build_context(
        self,
        query: str,
        token_budget: int = 4000,
        model: str = "gpt-4",
        weights: Optional[Dict[str, float]] = None,
        diversity_threshold: float = 0.7,
        min_score: Optional[float] = None,
        namespace: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Build intelligent context within token budget.
        
        Uses multi-factor scoring and diversity filtering.
        
        Args:
            query: Search query
            token_budget: Maximum tokens to use
            model: LLM model for token counting
            weights: Custom scoring weights (similarity, importance, recency, diversity)
            diversity_threshold: Jaccard similarity threshold (0-1)
            min_score: Minimum score filter (0-1)
            namespace: Optional namespace filter
            limit: Maximum candidate memories to retrieve
            
        Returns:
            Dictionary with 'memories' and 'metadata' keys
        """
    
    def format_context_for_llm(
        self,
        context: Dict[str, Any],
        include_scores: bool = False,
        include_timestamps: bool = True,
        separator: str = "\n\n"
    ) -> str:
        """Format context for LLM consumption.
        
        Args:
            context: Context from build_context()
            include_scores: Include score information
            include_timestamps: Include timestamps
            separator: Separator between memories
            
        Returns:
            Formatted string ready for LLM
        """
    
    def store_memory(
        self,
        content: str,
        importance_score: float = 0.5,
        memory_type: str = "semantic",
        metadata: Optional[Dict] = None,
        namespace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Store a new memory."""
    
    def query_memories(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.5
    ) -> Dict[str, Any]:
        """Simple semantic search (legacy method)."""
    
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get memory by ID."""
    
    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        importance_score: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update memory."""
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete memory."""
    
    def extract_memories(self, text: str) -> Dict[str, Any]:
        """Extract memories from raw text."""
    
    def create_namespace(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create namespace."""
    
    def grant_access(
        self,
        namespace_id: str,
        agent_id: str,
        permission: str = "read"
    ) -> Dict[str, Any]:
        """Grant namespace access."""
```

## Migration from v1.0.0

**Old way (simple concatenation):**
```python
results = client.query_memories("project launch", limit=20)
context = "\n".join([m["content"] for m in results["memories"]])
```

**New way (smart prioritization):**
```python
context_data = client.build_context(
    query="project launch",
    token_budget=2000  # Enforce budget
)
context = client.format_context_for_llm(context_data)
```

**Benefits:**
- ✅ Never exceeds token budget
- ✅ Better relevance (multi-factor scoring)
- ✅ Less redundancy (diversity filtering)
- ✅ Richer metadata (understand selections)

## Examples

### LangChain Integration

```python
from langchain.memory import ConversationBufferMemory
from vex_memory import VexMemoryClient

client = VexMemoryClient()

# Store conversation
def store_exchange(human_msg: str, ai_msg: str):
    client.store_memory(
        content=f"Human: {human_msg}\nAI: {ai_msg}",
        importance_score=0.6,
        memory_type="conversation"
    )

# Retrieve context
def get_relevant_context(query: str) -> str:
    context = client.build_context(
        query=query,
        token_budget=1500,  # Leave room for conversation
        model="gpt-3.5-turbo"
    )
    return client.format_context_for_llm(context)
```

### OpenClaw Integration

```python
from vex_memory import VexMemoryClient

client = VexMemoryClient()

# In your agent's session startup
def load_context(session_query: str):
    context = client.build_context(
        query=session_query,
        token_budget=6000,  # Budget for Claude Opus
        model="claude-3-opus",
        weights={
            "similarity": 0.3,
            "importance": 0.4,
            "recency": 0.3,
            "diversity": 0.0
        }
    )
    
    # Inject into session context
    formatted = client.format_context_for_llm(context, include_scores=False)
    return formatted
```

### Custom Weights for Different Use Cases

```python
# Recent events prioritized
recent_context = client.build_context(
    query="latest updates",
    weights={
        "similarity": 0.2,
        "importance": 0.2,
        "recency": 0.6,
        "diversity": 0.0
    }
)

# High-importance memories only
important_context = client.build_context(
    query="critical decisions",
    weights={
        "similarity": 0.3,
        "importance": 0.7,
        "recency": 0.0,
        "diversity": 0.0
    },
    min_score=0.7  # Filter low scores
)

# Maximum diversity
diverse_context = client.build_context(
    query="project overview",
    diversity_threshold=0.5,  # More aggressive
    weights={
        "similarity": 0.5,
        "importance": 0.3,
        "recency": 0.2,
        "diversity": 0.0
    }
)
```

## Error Handling

```python
from vex_memory import VexMemoryClient, VexMemoryError

client = VexMemoryClient()

try:
    context = client.build_context("query", token_budget=1000)
except VexMemoryError as e:
    print(f"API error: {e}")
    # Handle error
```

## Configuration

### Environment Variables

```bash
VEX_MEMORY_URL=http://localhost:8000
VEX_MEMORY_TIMEOUT=30
```

### Programmatic Configuration

```python
from vex_memory import VexMemoryClient

client = VexMemoryClient(
    base_url="http://my-server:8000",
    timeout=60  # Longer timeout for large queries
)
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy vex_memory

# Format code
black vex_memory tests
```

## License

MIT License - same as vex-memory main project.

## Links

- [vex-memory server](https://github.com/0x000NULL/vex-memory)
- [Documentation](https://vexmemory.dev)
- [Changelog](CHANGELOG.md)
