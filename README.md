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

## Auto-Tuning (v2.0.0)

**NEW:** vex-memory now learns optimal weights from your usage patterns!

### Enable Auto-Tuning

```python
from vex_memory import VexMemoryClient

client = VexMemoryClient()

# Enable auto-tuning for your namespace
client.enable_auto_tuning(
    namespace="my-agent",
    refresh_interval=3600  # Refresh learned weights every hour
)

# Now use build_context() normally
context = client.build_context(
    query="What are our deployment strategies?",
    token_budget=4000
)

# Automatically uses learned weights (if available)
# Falls back to defaults if no learned weights exist yet
```

### How It Works

1. **Usage Tracking**: Server logs every `build_context()` call (opt-in)
2. **Pattern Analysis**: System analyzes which weights work best
3. **Optimization**: Grid search finds optimal weights that maximize diversity + token efficiency
4. **Auto-Fetch**: SDK automatically fetches and uses learned weights

### Trigger Optimization

After 50+ queries, trigger weight optimization:

```python
result = client.trigger_weight_optimization(
    namespace="my-agent",
    min_queries=50  # Minimum historical queries required
)

print(f"Best weights: {result['best_weights']}")
print(f"Objective score: {result['objective_score']}")
# Output:
# Best weights: {'similarity': 0.45, 'importance': 0.35, 'recency': 0.2}
# Objective score: 1.28
```

### View Analytics

```python
summary = client.get_analytics_summary("my-agent")

print(f"Total queries: {summary['total_queries']}")
print(f"Avg token efficiency: {summary['avg_token_efficiency']:.2%}")
print(f"Avg computation time: {summary['avg_computation_time_ms']:.1f}ms")
```

### Export/Delete Analytics (GDPR)

```python
# Export data
data = client.export_analytics("my-agent", format="json")

# Delete all analytics data
result = client.delete_analytics("my-agent")
print(f"Deleted {result['deleted_logs']} query logs")
```

### Weight Priority

When you call `build_context()`, weights are selected in this order:

1. **Explicit user weights** (highest priority)
   ```python
   context = client.build_context("query", weights={"similarity": 0.5, ...})
   ```

2. **Learned weights** (if auto-tuning enabled)
   ```python
   client.enable_auto_tuning("my-agent")
   context = client.build_context("query")  # Uses learned weights
   ```

3. **Server defaults** (lowest priority)
   ```python
   context = client.build_context("query")  # Uses server defaults
   ```

### Privacy Controls

The server may be configured with privacy controls. See server's [PRIVACY.md](https://github.com/0x000NULL/vex-memory/blob/main/PRIVACY.md) for:

- Opting out of usage analytics
- Query sanitization (hashing)
- Data retention policies
- GDPR compliance

### Disable Auto-Tuning

```python
client.disable_auto_tuning()
```

### Complete Example

```python
from vex_memory import VexMemoryClient

# 1. Initialize
client = VexMemoryClient()

# 2. Use normally (analytics logged automatically)
for i in range(100):
    context = client.build_context(
        query=f"Query {i}",
        token_budget=4000,
        namespace="my-agent"
    )

# 3. Trigger optimization after 50+ queries
result = client.trigger_weight_optimization("my-agent")
print(f"Learned weights: {result['best_weights']}")

# 4. Enable auto-tuning
client.enable_auto_tuning("my-agent")

# 5. Continue using with optimized weights
context = client.build_context(
    query="Important query",
    token_budget=4000
)
# Now uses learned weights automatically!

# 6. Check improvement
summary = client.get_analytics_summary("my-agent")
print(f"Token efficiency: {summary['avg_token_efficiency']:.2%}")
```

### Auto-Tuning API Reference

#### `enable_auto_tuning(namespace, refresh_interval=3600)`

Enable automatic weight optimization.

- `namespace`: Namespace to optimize for
- `refresh_interval`: Seconds between weight refreshes (default: 1 hour)

#### `disable_auto_tuning()`

Disable auto-tuning and clear learned weights.

#### `get_learned_weights(namespace)`

Get current learned weights for a namespace.

Returns:
```python
{
    "id": "...",
    "namespace": "my-agent",
    "weights": {"similarity": 0.45, "importance": 0.35, "recency": 0.2},
    "objective_score": 1.28,
    "training_queries": 120,
    "optimization_method": "grid_search",
    "avg_diversity_score": 0.68,
    "avg_token_efficiency": 0.85,
    "created_at": "2026-03-01T10:00:00Z",
    "updated_at": "2026-03-01T10:00:00Z"
}
```

#### `trigger_weight_optimization(namespace, search_space=None, min_queries=50)`

Trigger weight optimization for a namespace.

- `namespace`: Namespace to optimize
- `search_space`: Optional custom search space (dict of param -> list of values)
- `min_queries`: Minimum historical queries required (default: 50)

Returns:
```python
{
    "weight_id": "...",
    "history_id": "...",
    "namespace": "my-agent",
    "best_weights": {...},
    "objective_score": 1.28,
    "metadata": {
        "training_queries": 120,
        "validation_queries": 30,
        "combinations_tested": 50,
        "computation_time_ms": 1250.5,
        "avg_diversity_score": 0.68,
        "avg_token_efficiency": 0.85
    }
}
```

#### `get_analytics_summary(namespace)`

Get usage analytics summary.

Returns:
```python
{
    "enabled": true,
    "namespace": "my-agent",
    "total_queries": 234,
    "avg_tokens_used": 3456.7,
    "avg_tokens_budget": 4000.0,
    "avg_token_efficiency": 0.864,
    "avg_memories_retrieved": 12.3,
    "avg_memories_dropped": 8.1,
    "avg_computation_time_ms": 42.5,
    "first_query": "2026-02-15T10:00:00Z",
    "last_query": "2026-03-01T08:00:00Z"
}
```

#### `export_analytics(namespace, format='json')`

Export analytics data for portability.

- `format`: "json" or "csv"

#### `delete_analytics(namespace)`

Delete all analytics data for a namespace (GDPR compliance).

Returns:
```python
{
    "namespace": "my-agent",
    "deleted_logs": 234,
    "message": "Deleted 234 query logs for namespace my-agent"
}
```

---

## Migration Guide

### From v1.2.0 to v2.0.0

**No breaking changes!** Auto-tuning is opt-in.

Existing code continues to work:
```python
# This still works exactly as before
context = client.build_context("query", token_budget=4000)
```

To use auto-tuning:
```python
# Enable auto-tuning (new in v2.0.0)
client.enable_auto_tuning(namespace="my-agent")

# Now this uses learned weights automatically
context = client.build_context("query", token_budget=4000)
```

