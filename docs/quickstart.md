# Quick Start Guide

Get started with vex-memory Python SDK in 5 minutes.

## Installation

```bash
pip install vex-memory
```

## Prerequisites

You need a running vex-memory server. The SDK connects to `http://localhost:8000` by default.

See [vex-memory server docs](https://github.com/0x000NULL/vex-memory) for installation.

## Your First Memory

```python
from vex_memory import MemoryClient

# Initialize client
client = MemoryClient("http://localhost:8000")

# Store a memory
memory = client.store("Python 3.12 was released in October 2023")
print(f"Stored: {memory.id}")

# Search
results = client.search("Python release")
for memory in results:
    print(f"Found: {memory.content}")
```

## Basic Operations

### Storing Memories

```python
# Simple
memory = client.store("Meeting notes from today")

# With metadata
memory = client.store(
    "Discussed Q2 roadmap with team",
    importance=0.8,
    metadata={
        "attendees": ["Alice", "Bob"],
        "date": "2026-02-28"
    }
)
```

### Searching

```python
# Simple search
results = client.search("what meetings?")

# With filters
results = client.search(
    "project updates",
    limit=20,
    min_score=0.7
)

# Find single best match
best = client.find_one("most important task")
```

### Updating & Deleting

```python
# Update
updated = client.update(
    memory_id,
    importance=0.9,
    metadata={"verified": True}
)

# Delete
client.delete(memory_id)
```

## Building Context for LLMs

```python
# Get relevant context
context = client.build_context(
    "What do I know about the project?",
    max_tokens=2000
)

# Use in LLM prompt
prompt = f"""
{context}

Based on the context above, what's the project status?
"""
```

## Bulk Operations

```python
# Store many at once
memories = client.store_many([
    "Note 1",
    "Note 2",
    {"content": "Note 3", "importance": 0.9}
])
```

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Examples](../examples/) - Working code examples
- [Advanced Patterns](advanced-usage.md) - Resource API, namespaces, sessions
