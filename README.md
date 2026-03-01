# vex-memory Python SDK

Official Python SDK for [vex-memory](https://github.com/0x000NULL/vex-memory) - A human-inspired memory system for AI agents.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- 🔍 **Semantic search** - Natural language queries with vector similarity
- 💾 **Memory management** - Store, retrieve, update, delete memories
- 🧠 **Context building** - Auto-format memories for LLM prompts
- 💬 **Session tracking** - Maintain conversation context
- 🏷️ **Namespaces** - Organize memories by scope
- ⚡ **Bulk operations** - Efficiently store multiple memories
- 🔄 **Auto-retry** - Resilient error handling with exponential backoff
- 🛡️ **Circuit breaker** - Prevent cascading failures (optional)
- 📝 **Type-safe** - Full Pydantic validation
- 🐍 **Pythonic** - Clean, intuitive API

## Installation

```bash
pip install vex-memory
```

For development:
```bash
pip install vex-memory[dev]
```

## Quick Start

### Simple Usage

```python
from vex_memory import MemoryClient

# Initialize client
client = MemoryClient("http://localhost:8000")

# Store memories
memory = client.store("Met with Alice to discuss Q2 roadmap")

# With metadata
memory = client.store(
    "Python 3.12 released with new features",
    importance=0.8,
    metadata={"category": "tech", "language": "python"}
)

# Search
results = client.search("What meetings did I have?")
for memory in results:
    print(f"{memory.content} (score: {memory.importance_score})")

# Build context for LLM
context = client.build_context("What do I know about the project?")
# Use in your LLM prompt
```

### Advanced Usage

```python
# Resource-based API
memory = client.memories.create(
    content="Important fact",
    importance=0.9,
    confidence=0.95
)

# Namespace organization
client.create_namespace("work", owner="agent-id")
client.use_namespace("work")

# All operations now use "work" namespace
work_memories = client.search("meetings")

# Or use context manager
with client.namespace("personal"):
    personal_memories = client.search("hobbies")

# Session management
session = client.create_session("chat-123")
client.add_to_session("chat-123", role="user", content="Hello!")
context = client.get_session_context("chat-123", max_tokens=2000)

# Bulk operations
memories = client.store_many([
    "Quick note 1",
    "Quick note 2",
    {"content": "Detailed note", "importance": 0.9}
])

# Context manager (recommended)
with MemoryClient() as client:
    memory = client.store("Note")
    results = client.search("query")
# Automatic cleanup
```

### Module-Level Shortcuts

For quick scripts and REPL usage:

```python
from vex_memory import store, search

# Uses default client from environment
store("Quick note")
results = search("what happened today?")
```

## Configuration

### From Code

```python
client = MemoryClient(
    base_url="http://localhost:8000",
    timeout=30,
    retry_attempts=3,
    enable_circuit_breaker=False,
    api_key="your-api-key"  # Optional
)
```

### From Environment

```python
# Reads from environment variables
client = MemoryClient.from_env()
```

Environment variables:
- `VEX_MEMORY_URL` - Server URL (default: http://localhost:8000)
- `VEX_MEMORY_API_KEY` - API key for authentication
- `VEX_MEMORY_TIMEOUT` - Request timeout in seconds (default: 30)
- `VEX_MEMORY_MAX_RETRIES` - Maximum retry attempts (default: 3)

## API Reference

### Core Client Methods

**Memory Operations:**
- `store(content, **kwargs)` - Store a memory
- `get(memory_id)` - Retrieve a memory by ID
- `update(memory_id, **kwargs)` - Update a memory
- `delete(memory_id)` - Delete a memory
- `store_many(memories)` - Bulk store memories

**Search & Query:**
- `search(query, limit=10, **filters)` - Semantic search
- `find_one(query, **filters)` - Find single best match
- `build_context(query, max_tokens=4000)` - Build LLM context

**Session Management:**
- `create_session(session_id)` - Create conversation session
- `get_session(session_id)` - Get session details
- `add_to_session(session_id, role, content)` - Add message
- `get_session_context(session_id, max_tokens)` - Get session context

**Namespaces:**
- `create_namespace(name, owner)` - Create namespace
- `list_namespaces()` - List all namespaces
- `use_namespace(namespace_id)` - Switch namespace
- `namespace(namespace_id)` - Context manager for temporary switch

**Admin:**
- `health()` - Check server health
- `stats()` - Get usage statistics

### Resource-Based API

For power users who prefer organized method grouping:

```python
# Memories
client.memories.create(content, **kwargs)
client.memories.get(memory_id)
client.memories.list(limit=10, **filters)
client.memories.update(memory_id, **kwargs)
client.memories.delete(memory_id)
client.memories.bulk_create(memories)
client.memories.stream(chunk_size=100)  # For large datasets

# Queries
client.queries.search(query, limit=10, **filters)
client.queries.find_one(query, **filters)
client.queries.build_context(query, max_tokens=4000)

# Namespaces
client.namespaces.create(name, owner)
client.namespaces.list()
client.namespaces.grant_access(namespace_id, agent_id, permissions)

# Sessions
client.sessions.create(session_id)
client.sessions.get(session_id)
client.sessions.add_message(session_id, role, content)
client.sessions.get_context(session_id, max_tokens)
```

## Examples

See the [examples/](./examples) directory for complete working examples:

- `01_basic_usage.py` - Simple memory storage and search
- `02_context_building.py` - Building context for LLM prompts
- `03_sessions.py` - Conversation session management
- `04_namespaces.py` - Organizing memories with namespaces
- `05_bulk_operations.py` - Efficient bulk operations
- `06_error_handling.py` - Robust error handling
- `07_advanced_patterns.py` - Advanced usage patterns

## Compatibility

| SDK Version | Server Version |
|-------------|----------------|
| 1.0.x       | 0.3.0+         |

## Error Handling

The SDK provides clear exceptions for different error conditions:

```python
from vex_memory import (
    MemoryClient,
    ConnectionError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError,
    TimeoutError,
)

try:
    memory = client.get("invalid-id")
except NotFoundError:
    print("Memory not found")
except ConnectionError:
    print("Cannot connect to server")
except TimeoutError:
    print("Request timed out")
```

## Development

### Setup

```bash
git clone https://github.com/0x000NULL/vex-memory-sdk.git
cd vex-memory-sdk
pip install -e ".[dev]"
```

### Running Tests

```bash
# Unit tests
pytest tests/unit -v

# Integration tests (requires running server)
pytest tests/integration -v

# All tests with coverage
pytest --cov=vex_memory --cov-report=html
```

### Code Quality

```bash
# Format code
black vex_memory tests

# Lint
flake8 vex_memory tests

# Type check
mypy vex_memory --strict
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Tests pass (`pytest`)
- Code is formatted (`black`)
- Type checking passes (`mypy`)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **Server**: [vex-memory](https://github.com/0x000NULL/vex-memory)
- **Documentation**: [docs/](./docs)
- **Issues**: [GitHub Issues](https://github.com/0x000NULL/vex-memory-sdk/issues)
- **PyPI**: [vex-memory](https://pypi.org/project/vex-memory/) (coming soon)

## Support

- 📧 Email: e.aldrich@budgetlasvegas.com
- 🐛 Issues: [GitHub Issues](https://github.com/0x000NULL/vex-memory-sdk/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/0x000NULL/vex-memory-sdk/discussions)
