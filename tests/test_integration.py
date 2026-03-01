"""
Integration tests against live vex-memory server.

These tests require a running vex-memory server at http://localhost:8000
"""

import pytest
from vex_memory import MemoryClient, Memory, NotFoundError


# Skip integration tests if server not available
pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    """Create client for integration tests."""
    return MemoryClient("http://localhost:8000")


def test_full_memory_lifecycle(client):
    """Test complete memory CRUD lifecycle."""
    # Create
    memory = client.store(
        "Integration test memory",
        importance=0.7,
        metadata={"test": True, "source": "pytest"}
    )
    
    assert memory.id is not None
    assert memory.content == "Integration test memory"
    assert memory.importance_score == 0.7
    
    memory_id = memory.id
    
    # Read
    retrieved = client.get(memory_id)
    assert retrieved.id == memory_id
    assert retrieved.content == "Integration test memory"
    
    # Update
    updated = client.update(
        memory_id,
        importance=0.9,
        metadata={"test": True, "updated": True}
    )
    assert updated.importance_score == 0.9
    
    # Delete
    success = client.delete(memory_id)
    assert success is True
    
    # Verify deleted
    with pytest.raises(NotFoundError):
        client.get(memory_id)


def test_search(client):
    """Test semantic search."""
    # Store test data
    mem1 = client.store("The sky is blue", metadata={"test": True})
    mem2 = client.store("Grass is green", metadata={"test": True})
    mem3 = client.store("Water is wet", metadata={"test": True})
    
    try:
        # Search
        results = client.search("colors", limit=10)
        
        assert len(results) > 0
        assert isinstance(results[0], Memory)
        
        # Cleanup
        client.delete(mem1.id)
        client.delete(mem2.id)
        client.delete(mem3.id)
    except Exception as e:
        # Cleanup even on failure
        try:
            client.delete(mem1.id)
            client.delete(mem2.id)
            client.delete(mem3.id)
        except:
            pass
        raise e


def test_bulk_operations(client):
    """Test bulk memory creation."""
    memories_data = [
        "Bulk test 1",
        "Bulk test 2",
        {"content": "Bulk test 3", "importance": 0.8}
    ]
    
    memories = client.store_many(memories_data)
    
    assert len(memories) == 3
    assert all(isinstance(m, Memory) for m in memories)
    
    # Cleanup
    for memory in memories:
        client.delete(memory.id)


def test_context_building(client):
    """Test building context for LLM."""
    # Store knowledge base
    facts = [
        "Project Alpha uses Python 3.11",
        "Alice is the tech lead",
        "Beta release planned for Q2",
    ]
    
    stored = [client.store(fact, metadata={"test": True}) for fact in facts]
    
    try:
        # Build context
        context = client.build_context("What is Project Alpha?", max_tokens=1000)
        
        assert isinstance(context, str)
        assert len(context) > 0
        
        # Cleanup
        for memory in stored:
            client.delete(memory.id)
    except Exception as e:
        # Cleanup even on failure
        for memory in stored:
            try:
                client.delete(memory.id)
            except:
                pass
        raise e


def test_health_check(client):
    """Test server health endpoint."""
    health = client.health()
    
    assert health.status in ["healthy", "ok"]
    # Version is optional in current API
    assert health.memory_count is not None


def test_stats(client):
    """Test server stats endpoint."""
    stats = client.stats()
    
    assert stats.total_memories >= 0
    assert stats.total_entities is not None
    assert stats.memory_types is not None


def test_context_manager(client):
    """Test context manager usage."""
    with MemoryClient("http://localhost:8000") as temp_client:
        memory = temp_client.store("Context manager test")
        assert memory.id is not None
        
        # Cleanup
        temp_client.delete(memory.id)


if __name__ == "__main__":
    # Run integration tests manually
    pytest.main([__file__, "-v", "-m", "integration"])
