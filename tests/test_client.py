"""
Unit tests for MemoryClient.
"""

import pytest
from unittest.mock import Mock, patch
from vex_memory import MemoryClient, Memory, NotFoundError


class TestMemoryClient:
    """Test MemoryClient core functionality."""
    
    def test_initialization(self):
        """Test client initialization."""
        client = MemoryClient("http://test:8000")
        assert client.base_url == "http://test:8000"
        assert client.timeout == 30
        assert client.retry_attempts == 3
    
    def test_initialization_with_trailing_slash(self):
        """Test URL normalization."""
        client = MemoryClient("http://test:8000/")
        assert client.base_url == "http://test:8000"
    
    def test_context_manager(self):
        """Test context manager support."""
        with MemoryClient("http://test:8000") as client:
            assert client is not None
        # Session should be closed after exit
    
    @patch('vex_memory.client.requests.Session')
    def test_store_memory(self, mock_session_class):
        """Test storing a memory."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "mem-123",
            "type": "semantic",
            "content": "Test memory",
            "importance_score": 0.5,
            "confidence_score": 0.8,
            "decay_factor": 1.0,
            "access_count": 0,
            "metadata": {}
        }
        mock_response.content = True
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Test
        client = MemoryClient("http://test:8000")
        memory = client.store("Test memory")
        
        assert isinstance(memory, Memory)
        assert memory.id == "mem-123"
        assert memory.content == "Test memory"
    
    @patch('vex_memory.client.requests.Session')
    def test_search(self, mock_session_class):
        """Test searching memories."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "memories": [
                {
                    "id": "mem-1",
                    "type": "semantic",
                    "content": "Test 1",
                    "importance_score": 0.8,
                    "confidence_score": 0.9,
                    "decay_factor": 1.0,
                    "access_count": 1,
                    "metadata": {}
                },
                {
                    "id": "mem-2",
                    "type": "semantic",
                    "content": "Test 2",
                    "importance_score": 0.7,
                    "confidence_score": 0.8,
                    "decay_factor": 1.0,
                    "access_count": 2,
                    "metadata": {}
                }
            ]
        }
        mock_response.content = True
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Test
        client = MemoryClient("http://test:8000")
        results = client.search("test query")
        
        assert len(results) == 2
        assert isinstance(results[0], Memory)
        assert results[0].content == "Test 1"
    
    def test_from_env(self, monkeypatch):
        """Test client creation from environment."""
        monkeypatch.setenv("VEX_MEMORY_URL", "http://env-test:9000")
        monkeypatch.setenv("VEX_MEMORY_TIMEOUT", "60")
        monkeypatch.setenv("VEX_MEMORY_MAX_RETRIES", "5")
        
        client = MemoryClient.from_env()
        
        assert client.base_url == "http://env-test:9000"
        assert client.timeout == 60
        assert client.retry_attempts == 5
    
    def test_namespace_context_manager(self):
        """Test namespace context manager."""
        client = MemoryClient("http://test:8000")
        
        assert client._current_namespace is None
        
        with client.namespace("test-ns"):
            assert client._current_namespace == "test-ns"
        
        # Should restore to None
        assert client._current_namespace is None
    
    def test_use_namespace(self):
        """Test switching namespaces."""
        client = MemoryClient("http://test:8000")
        
        client.use_namespace("work")
        assert client._current_namespace == "work"
        
        client.use_namespace("personal")
        assert client._current_namespace == "personal"


class TestResourceAPIs:
    """Test resource-based API access."""
    
    def test_memories_resource(self):
        """Test memories resource."""
        client = MemoryClient("http://test:8000")
        assert client.memories is not None
        assert hasattr(client.memories, 'create')
        assert hasattr(client.memories, 'get')
        assert hasattr(client.memories, 'list')
    
    def test_queries_resource(self):
        """Test queries resource."""
        client = MemoryClient("http://test:8000")
        assert client.queries is not None
        assert hasattr(client.queries, 'search')
        assert hasattr(client.queries, 'find_one')
    
    def test_namespaces_resource(self):
        """Test namespaces resource."""
        client = MemoryClient("http://test:8000")
        assert client.namespaces is not None
        assert hasattr(client.namespaces, 'create')
        assert hasattr(client.namespaces, 'list')
    
    def test_sessions_resource(self):
        """Test sessions resource."""
        client = MemoryClient("http://test:8000")
        assert client.sessions is not None
        assert hasattr(client.sessions, 'create')
        assert hasattr(client.sessions, 'get')
