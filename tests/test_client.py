"""
Unit tests for VexMemoryClient
"""

import pytest
import responses
from datetime import datetime
from vex_memory import VexMemoryClient, VexMemoryAPIError, VexMemoryValidationError


@pytest.fixture
def client():
    """Create test client."""
    return VexMemoryClient(base_url="http://test-server:8000", timeout=10)


class TestClientInitialization:
    """Test client initialization."""
    
    def test_init_default(self):
        """Test default initialization."""
        client = VexMemoryClient()
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 30
    
    def test_init_custom(self):
        """Test custom initialization."""
        client = VexMemoryClient(
            base_url="http://custom:9000",
            timeout=60
        )
        assert client.base_url == "http://custom:9000"
        assert client.timeout == 60
    
    def test_init_strips_trailing_slash(self):
        """Test that trailing slashes are removed."""
        client = VexMemoryClient(base_url="http://test:8000/")
        assert client.base_url == "http://test:8000"


class TestBuildContext:
    """Test build_context method."""
    
    @responses.activate
    def test_build_context_basic(self, client):
        """Test basic context building."""
        # Mock API response
        responses.add(
            responses.POST,
            "http://test-server:8000/api/memories/prioritized-context",
            json={
                "memories": [
                    {
                        "id": "mem-1",
                        "content": "Test memory",
                        "importance_score": 0.8,
                        "_score": 0.75
                    }
                ],
                "metadata": {
                    "total_tokens": 150,
                    "budget": 2000,
                    "utilization": 0.075
                }
            },
            status=200
        )
        
        result = client.build_context("test query", token_budget=2000)
        
        assert len(result["memories"]) == 1
        assert result["metadata"]["total_tokens"] == 150
        assert responses.calls[0].request.url == "http://test-server:8000/api/memories/prioritized-context"
    
    @responses.activate
    def test_build_context_with_custom_weights(self, client):
        """Test context building with custom weights."""
        responses.add(
            responses.POST,
            "http://test-server:8000/api/memories/prioritized-context",
            json={"memories": [], "metadata": {}},
            status=200
        )
        
        weights = {
            "similarity": 0.5,
            "importance": 0.3,
            "recency": 0.2,
            "diversity": 0.0
        }
        
        client.build_context("test", weights=weights)
        
        # Verify request payload
        import json
        request_body = json.loads(responses.calls[0].request.body)
        assert request_body["weights"] == weights
    
    def test_build_context_validation_empty_query(self, client):
        """Test validation for empty query."""
        with pytest.raises(VexMemoryValidationError, match="Query cannot be empty"):
            client.build_context("")
    
    def test_build_context_validation_negative_budget(self, client):
        """Test validation for negative token budget."""
        with pytest.raises(VexMemoryValidationError, match="Token budget must be positive"):
            client.build_context("test", token_budget=-100)
    
    def test_build_context_validation_invalid_threshold(self, client):
        """Test validation for invalid diversity threshold."""
        with pytest.raises(VexMemoryValidationError, match="Diversity threshold"):
            client.build_context("test", diversity_threshold=1.5)
    
    def test_build_context_validation_invalid_min_score(self, client):
        """Test validation for invalid min score."""
        with pytest.raises(VexMemoryValidationError, match="Min score"):
            client.build_context("test", min_score=-0.1)


class TestFormatContextForLLM:
    """Test context formatting."""
    
    def test_format_basic(self, client):
        """Test basic formatting."""
        context = {
            "memories": [
                {"id": "1", "content": "First memory"},
                {"id": "2", "content": "Second memory"}
            ],
            "metadata": {}
        }
        
        result = client.format_context_for_llm(context)
        
        assert "First memory" in result
        assert "Second memory" in result
        assert result.count("\n\n") == 1  # One separator
    
    def test_format_with_timestamps(self, client):
        """Test formatting with timestamps."""
        context = {
            "memories": [
                {
                    "id": "1",
                    "content": "Memory content",
                    "event_time": "2024-01-15T10:30:00Z"
                }
            ],
            "metadata": {}
        }
        
        result = client.format_context_for_llm(context, include_timestamps=True)
        
        assert "[2024-01-15]" in result
        assert "Memory content" in result
    
    def test_format_with_scores(self, client):
        """Test formatting with scores."""
        context = {
            "memories": [
                {
                    "id": "1",
                    "content": "Test",
                    "_score": 0.85,
                    "importance_score": 0.9
                }
            ],
            "metadata": {}
        }
        
        result = client.format_context_for_llm(context, include_scores=True)
        
        assert "score: 0.85" in result
        assert "importance: 0.90" in result
    
    def test_format_empty_context(self, client):
        """Test formatting empty context."""
        context = {"memories": [], "metadata": {}}
        
        result = client.format_context_for_llm(context)
        
        assert result == ""
    
    def test_format_custom_separator(self, client):
        """Test custom separator."""
        context = {
            "memories": [
                {"id": "1", "content": "First"},
                {"id": "2", "content": "Second"}
            ],
            "metadata": {}
        }
        
        result = client.format_context_for_llm(context, separator="\n---\n")
        
        assert "\n---\n" in result


class TestStoreMemory:
    """Test store_memory method."""
    
    @responses.activate
    def test_store_memory_basic(self, client):
        """Test basic memory storage."""
        responses.add(
            responses.POST,
            "http://test-server:8000/api/memory",
            json={
                "id": "mem-123",
                "content": "Test memory",
                "importance_score": 0.7
            },
            status=200
        )
        
        result = client.store_memory(
            content="Test memory",
            importance_score=0.7
        )
        
        assert result["id"] == "mem-123"
        assert result["content"] == "Test memory"
    
    def test_store_memory_validation_empty_content(self, client):
        """Test validation for empty content."""
        with pytest.raises(VexMemoryValidationError, match="Content cannot be empty"):
            client.store_memory(content="")
    
    def test_store_memory_validation_invalid_score(self, client):
        """Test validation for invalid importance score."""
        with pytest.raises(VexMemoryValidationError, match="Importance score"):
            client.store_memory(content="Test", importance_score=1.5)


class TestQueryMemories:
    """Test query_memories method."""
    
    @responses.activate
    def test_query_basic(self, client):
        """Test basic query."""
        responses.add(
            responses.POST,
            "http://test-server:8000/api/query",
            json={
                "memories": [
                    {"id": "1", "content": "Result 1"},
                    {"id": "2", "content": "Result 2"}
                ]
            },
            status=200
        )
        
        result = client.query_memories("test query", limit=10)
        
        assert len(result["memories"]) == 2


class TestGetMemory:
    """Test get_memory method."""
    
    @responses.activate
    def test_get_memory_success(self, client):
        """Test successful memory retrieval."""
        responses.add(
            responses.GET,
            "http://test-server:8000/api/memory/mem-123",
            json={
                "id": "mem-123",
                "content": "Test memory"
            },
            status=200
        )
        
        result = client.get_memory("mem-123")
        
        assert result["id"] == "mem-123"
    
    @responses.activate
    def test_get_memory_not_found(self, client):
        """Test memory not found."""
        responses.add(
            responses.GET,
            "http://test-server:8000/api/memory/nonexistent",
            json={"detail": "Memory not found"},
            status=404
        )
        
        with pytest.raises(VexMemoryAPIError) as exc_info:
            client.get_memory("nonexistent")
        
        assert exc_info.value.status_code == 404


class TestUpdateMemory:
    """Test update_memory method."""
    
    @responses.activate
    def test_update_memory(self, client):
        """Test memory update."""
        responses.add(
            responses.PUT,
            "http://test-server:8000/api/memory/mem-123",
            json={
                "id": "mem-123",
                "content": "Updated content",
                "importance_score": 0.9
            },
            status=200
        )
        
        result = client.update_memory(
            "mem-123",
            content="Updated content",
            importance_score=0.9
        )
        
        assert result["content"] == "Updated content"


class TestDeleteMemory:
    """Test delete_memory method."""
    
    @responses.activate
    def test_delete_memory(self, client):
        """Test memory deletion."""
        responses.add(
            responses.DELETE,
            "http://test-server:8000/api/memory/mem-123",
            status=200
        )
        
        result = client.delete_memory("mem-123")
        
        assert result is True


class TestNamespaces:
    """Test namespace operations."""
    
    @responses.activate
    def test_create_namespace(self, client):
        """Test namespace creation."""
        responses.add(
            responses.POST,
            "http://test-server:8000/api/namespace",
            json={
                "namespace_id": "ns-123",
                "name": "test-namespace"
            },
            status=200
        )
        
        result = client.create_namespace(name="test-namespace")
        
        assert result["namespace_id"] == "ns-123"
    
    @responses.activate
    def test_grant_access(self, client):
        """Test access grant."""
        responses.add(
            responses.POST,
            "http://test-server:8000/api/namespace/grant",
            json={"success": True},
            status=200
        )
        
        result = client.grant_access(
            namespace_id="ns-123",
            agent_id="agent-456",
            permission="write"
        )
        
        assert result["success"] is True


class TestMMR:
    """Test MMR (Maximal Marginal Relevance) functionality."""
    
    @responses.activate
    def test_build_context_with_mmr(self, client):
        """Test context building with MMR."""
        responses.add(
            responses.POST,
            "http://test-server:8000/api/memories/prioritized-mmr",
            json={
                "memories": [
                    {
                        "id": "mem-1",
                        "content": "First memory",
                        "importance_score": 0.9
                    }
                ],
                "metadata": {
                    "total_tokens": 50,
                    "method": "mmr",
                    "lambda": 0.7
                }
            },
            status=200
        )
        
        result = client.build_context(
            query="test query",
            use_mmr=True,
            mmr_lambda=0.7
        )
        
        assert len(result["memories"]) == 1
        assert result["metadata"]["method"] == "mmr"
        assert result["metadata"]["lambda"] == 0.7
    
    @responses.activate
    def test_build_context_mmr_custom_lambda(self, client):
        """Test MMR with custom lambda parameter."""
        responses.add(
            responses.POST,
            "http://test-server:8000/api/memories/prioritized-mmr",
            json={
                "memories": [],
                "metadata": {"total_tokens": 0, "method": "mmr", "lambda": 0.3}
            },
            status=200
        )
        
        result = client.build_context(
            query="test",
            use_mmr=True,
            mmr_lambda=0.3  # More diversity
        )
        
        assert result["metadata"]["lambda"] == 0.3
    
    def test_mmr_lambda_validation(self, client):
        """Test MMR lambda parameter validation."""
        with pytest.raises(VexMemoryValidationError):
            client.build_context(query="test", use_mmr=True, mmr_lambda=1.5)
        
        with pytest.raises(VexMemoryValidationError):
            client.build_context(query="test", use_mmr=True, mmr_lambda=-0.1)


class TestWeightPresets:
    """Test weight preset functionality."""
    
    @responses.activate
    def test_get_weight_presets(self, client):
        """Test getting available weight presets."""
        responses.add(
            responses.GET,
            "http://test-server:8000/api/weights/presets",
            json={
                "presets": [
                    {
                        "name": "Balanced",
                        "key": "balanced",
                        "description": "Balanced across all factors"
                    },
                    {
                        "name": "Relevance Focused",
                        "key": "relevance_focused",
                        "description": "Prioritizes similarity"
                    }
                ]
            },
            status=200
        )
        
        result = client.get_weight_presets()
        
        assert "presets" in result
        assert len(result["presets"]) == 2
        assert result["presets"][0]["key"] == "balanced"
    
    @responses.activate
    def test_get_recommended_weights(self, client):
        """Test getting recommended weights for a use case."""
        responses.add(
            responses.GET,
            "http://test-server:8000/api/weights/recommend",
            json={
                "name": "Entity Focused",
                "description": "Prioritizes entity coverage",
                "weights": {
                    "similarity": 0.3,
                    "importance": 0.25,
                    "recency": 0.1,
                    "diversity": 0.1,
                    "entity_coverage": 0.25
                }
            },
            status=200
        )
        
        result = client.get_recommended_weights(use_case="entity_focused")
        
        assert result["name"] == "Entity Focused"
        assert result["weights"]["entity_coverage"] == 0.25
    
    @responses.activate
    def test_get_recommended_weights_default(self, client):
        """Test getting recommended weights with default use case."""
        responses.add(
            responses.GET,
            "http://test-server:8000/api/weights/recommend",
            json={
                "name": "Balanced",
                "weights": {
                    "similarity": 0.35,
                    "importance": 0.3,
                    "recency": 0.2,
                    "diversity": 0.1,
                    "entity_coverage": 0.05
                }
            },
            status=200
        )
        
        result = client.get_recommended_weights()
        
        assert result["name"] == "Balanced"
    
    @responses.activate
    def test_build_context_with_preset_weights(self, client):
        """Test using preset weights in build_context."""
        # First get the preset
        responses.add(
            responses.GET,
            "http://test-server:8000/api/weights/recommend",
            json={
                "name": "Relevance Focused",
                "weights": {
                    "similarity": 0.6,
                    "importance": 0.25,
                    "recency": 0.1,
                    "diversity": 0.03,
                    "entity_coverage": 0.02
                }
            },
            status=200
        )
        
        # Then use it in build_context
        responses.add(
            responses.POST,
            "http://test-server:8000/api/memories/prioritized-context",
            json={
                "memories": [{"id": "mem-1", "content": "Test"}],
                "metadata": {"total_tokens": 10}
            },
            status=200
        )
        
        # Get recommended weights
        preset = client.get_recommended_weights("relevance_focused")
        
        # Use them in context building
        result = client.build_context(
            query="test",
            weights=preset["weights"]
        )
        
        assert len(result["memories"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
