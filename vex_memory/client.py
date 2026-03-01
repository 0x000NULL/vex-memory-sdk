"""
Vex Memory Client - Main SDK interface
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

from .exceptions import VexMemoryAPIError, VexMemoryValidationError


class VexMemoryClient:
    """Client for vex-memory API with intelligent context building."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        """Initialize vex-memory client.
        
        Args:
            base_url: Base URL of vex-memory API (default: env VEX_MEMORY_URL or localhost:8000)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = (
            base_url or
            os.getenv("VEX_MEMORY_URL", "http://localhost:8000")
        ).rstrip("/")
        
        self.timeout = int(os.getenv("VEX_MEMORY_TIMEOUT", str(timeout)))
        self.session = requests.Session()
    
    def build_context(
        self,
        query: str,
        token_budget: int = 4000,
        model: str = "gpt-4",
        weights: Optional[Dict[str, float]] = None,
        diversity_threshold: float = 0.7,
        min_score: Optional[float] = None,
        namespace: Optional[str] = None,
        limit: int = 100,
        use_mmr: bool = False,
        mmr_lambda: float = 0.7
    ) -> Dict[str, Any]:
        """Build intelligent context within token budget.
        
        Uses multi-factor scoring (similarity, importance, recency) with diversity
        filtering to select the most relevant memories within the token budget.
        
        Args:
            query: Search query for finding relevant memories
            token_budget: Maximum tokens to use (default: 4000)
            model: LLM model for token counting (default: "gpt-4")
            weights: Custom scoring weights dict with keys: similarity, importance, recency, diversity
            diversity_threshold: Jaccard similarity threshold for filtering (0-1, default: 0.7)
            min_score: Minimum composite score threshold (0-1, optional)
            namespace: Optional namespace UUID filter
            limit: Maximum candidate memories to retrieve (default: 100)
            use_mmr: Use Maximal Marginal Relevance for selection (default: False)
            mmr_lambda: MMR balance between relevance (1.0) and diversity (0.0) (default: 0.7)
            
        Returns:
            Dictionary with keys:
                - memories: List of selected memory dictionaries
                - metadata: Selection metadata (tokens, utilization, scores, etc.)
                
        Raises:
            VexMemoryValidationError: Invalid parameters
            VexMemoryAPIError: API request failed
        """
        # Validate parameters
        if not query:
            raise VexMemoryValidationError("Query cannot be empty")
        
        if token_budget <= 0:
            raise VexMemoryValidationError("Token budget must be positive")
        
        if not (0.0 <= diversity_threshold <= 1.0):
            raise VexMemoryValidationError("Diversity threshold must be between 0 and 1")
        
        if min_score is not None and not (0.0 <= min_score <= 1.0):
            raise VexMemoryValidationError("Min score must be between 0 and 1")
        
        if not (0.0 <= mmr_lambda <= 1.0):
            raise VexMemoryValidationError("MMR lambda must be between 0 and 1")
        
        # Build request payload
        payload = {
            "query": query,
            "token_budget": token_budget,
            "model": model,
            "diversity_threshold": diversity_threshold,
            "limit": limit
        }
        
        if weights is not None:
            payload["weights"] = weights
        
        if min_score is not None:
            payload["min_score"] = min_score
        
        if namespace is not None:
            payload["namespace"] = namespace
        
        # Choose endpoint based on use_mmr
        if use_mmr:
            # Add lambda parameter for MMR
            if "weights" not in payload:
                payload["weights"] = {}
            payload["weights"]["lambda"] = mmr_lambda
            
            # Make request to MMR endpoint
            return self._post("/api/memories/prioritized-mmr", payload)
        else:
            # Make request to standard prioritization endpoint
            return self._post("/api/memories/prioritized-context", payload)
    
    def format_context_for_llm(
        self,
        context: Dict[str, Any],
        include_scores: bool = False,
        include_timestamps: bool = True,
        separator: str = "\n\n"
    ) -> str:
        """Format context for LLM consumption.
        
        Args:
            context: Context dictionary from build_context()
            include_scores: Include score information in output
            include_timestamps: Include event timestamps
            separator: Separator between memories (default: double newline)
            
        Returns:
            Formatted string ready for LLM
        """
        memories = context.get("memories", [])
        
        if not memories:
            return ""
        
        formatted_parts = []
        
        for memory in memories:
            parts = []
            
            # Timestamp
            if include_timestamps and memory.get("event_time"):
                event_time = memory["event_time"]
                if isinstance(event_time, str):
                    # Parse ISO format
                    try:
                        dt = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
                        parts.append(f"[{dt.strftime('%Y-%m-%d')}]")
                    except (ValueError, AttributeError):
                        pass
                elif hasattr(event_time, 'strftime'):
                    parts.append(f"[{event_time.strftime('%Y-%m-%d')}]")
            
            # Content
            parts.append(memory.get("content", ""))
            
            # Scores
            if include_scores:
                score_info = []
                
                if "_score" in memory:
                    score_info.append(f"score: {memory['_score']:.2f}")
                
                if memory.get("importance_score"):
                    score_info.append(f"importance: {memory['importance_score']:.2f}")
                
                if score_info:
                    parts.append(f"({', '.join(score_info)})")
            
            formatted_parts.append(" ".join(parts))
        
        return separator.join(formatted_parts)
    
    def store_memory(
        self,
        content: str,
        importance_score: float = 0.5,
        memory_type: str = "semantic",
        metadata: Optional[Dict] = None,
        namespace_id: Optional[str] = None,
        event_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Store a new memory.
        
        Args:
            content: Memory content text
            importance_score: Importance score (0-1, default: 0.5)
            memory_type: Memory type (semantic, episodic, etc., default: "semantic")
            metadata: Optional metadata dictionary
            namespace_id: Optional namespace UUID
            event_time: Optional event timestamp (ISO format or datetime)
            
        Returns:
            Created memory dictionary
            
        Raises:
            VexMemoryValidationError: Invalid parameters
            VexMemoryAPIError: API request failed
        """
        if not content:
            raise VexMemoryValidationError("Content cannot be empty")
        
        if not (0.0 <= importance_score <= 1.0):
            raise VexMemoryValidationError("Importance score must be between 0 and 1")
        
        payload = {
            "content": content,
            "importance_score": importance_score,
            "type": memory_type
        }
        
        if metadata is not None:
            payload["metadata"] = metadata
        
        if namespace_id is not None:
            payload["namespace_id"] = namespace_id
        
        if event_time is not None:
            if isinstance(event_time, datetime):
                payload["event_time"] = event_time.isoformat()
            else:
                payload["event_time"] = event_time
        
        return self._post("/api/memory", payload)
    
    def query_memories(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.5
    ) -> Dict[str, Any]:
        """Simple semantic search (legacy method).
        
        For better results, use build_context() instead.
        
        Args:
            query: Search query
            limit: Maximum memories to return (default: 10)
            min_similarity: Minimum cosine similarity (0-1, default: 0.5)
            
        Returns:
            Dictionary with memories and metadata
        """
        payload = {
            "query": query,
            "limit": limit,
            "min_similarity": min_similarity
        }
        
        return self._post("/api/query", payload)
    
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get memory by ID.
        
        Args:
            memory_id: Memory UUID
            
        Returns:
            Memory dictionary
            
        Raises:
            VexMemoryAPIError: Memory not found or request failed
        """
        return self._get(f"/api/memory/{memory_id}")
    
    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        importance_score: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update memory.
        
        Args:
            memory_id: Memory UUID
            content: New content (optional)
            importance_score: New importance score (optional)
            metadata: New metadata (optional)
            
        Returns:
            Updated memory dictionary
        """
        payload = {}
        
        if content is not None:
            payload["content"] = content
        
        if importance_score is not None:
            if not (0.0 <= importance_score <= 1.0):
                raise VexMemoryValidationError("Importance score must be between 0 and 1")
            payload["importance_score"] = importance_score
        
        if metadata is not None:
            payload["metadata"] = metadata
        
        return self._put(f"/api/memory/{memory_id}", payload)
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete memory.
        
        Args:
            memory_id: Memory UUID
            
        Returns:
            True if deleted successfully
        """
        self._delete(f"/api/memory/{memory_id}")
        return True
    
    def extract_memories(self, text: str) -> Dict[str, Any]:
        """Extract memories from raw text using NLP.
        
        Args:
            text: Raw text to extract from
            
        Returns:
            Dictionary with extracted memories
        """
        response = self._post("/extract", data={"content": text}, use_params=True)
        return response
    
    def create_namespace(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a new namespace.
        
        Args:
            name: Namespace name
            description: Optional description
            metadata: Optional metadata
            
        Returns:
            Created namespace dictionary
        """
        payload = {"name": name}
        
        if description is not None:
            payload["description"] = description
        
        if metadata is not None:
            payload["metadata"] = metadata
        
        return self._post("/api/namespace", payload)
    
    def list_namespaces(
        self,
        agent_id: Optional[str] = None,
        permission: str = "read"
    ) -> List[Dict[str, Any]]:
        """List namespaces.
        
        Args:
            agent_id: Filter by agent ID (optional)
            permission: Filter by permission (default: "read")
            
        Returns:
            List of namespace dictionaries
        """
        params = {"permission": permission}
        
        if agent_id is not None:
            params["agent_id"] = agent_id
        
        return self._get("/api/namespaces", params=params)
    
    def grant_access(
        self,
        namespace_id: str,
        agent_id: str,
        permission: str = "read"
    ) -> Dict[str, Any]:
        """Grant namespace access to an agent.
        
        Args:
            namespace_id: Namespace UUID
            agent_id: Agent identifier
            permission: Permission type ("read" or "write", default: "read")
            
        Returns:
            Updated access policy
        """
        payload = {
            "namespace_id": namespace_id,
            "agent_id": agent_id,
            "permission": permission
        }
        
        return self._post("/api/namespace/grant", payload)
    
    # Weight configuration methods (v1.2.0)
    
    def get_weight_presets(self) -> Dict[str, Any]:
        """Get available weight preset configurations.
        
        Returns list of preset configurations for different use cases
        (balanced, relevance_focused, recency_focused, etc.)
        
        Returns:
            Dictionary with 'presets' key containing list of preset info
            
        Raises:
            VexMemoryAPIError: API request failed
        """
        return self._get("/api/weights/presets")
    
    def get_recommended_weights(self, use_case: str = "balanced") -> Dict[str, Any]:
        """Get recommended weights for a specific use case.
        
        Available use cases:
        - balanced: Balanced across all factors
        - relevance_focused: Prioritizes similarity and importance
        - recency_focused: Prioritizes recent memories
        - diversity_focused: Maximizes variety and coverage
        - entity_focused: Prioritizes entity coverage
        - importance_focused: Prioritizes memory importance
        
        Args:
            use_case: Use case identifier (default: "balanced")
            
        Returns:
            Weight configuration dictionary with name, description, and weights
            
        Raises:
            VexMemoryAPIError: API request failed
        """
        return self._get("/api/weights/recommend", params={"use_case": use_case})
    
    # Internal HTTP methods
    
    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        """Make GET request."""
        url = f"{self.base_url}{path}"
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            raise VexMemoryAPIError(f"Request failed: {str(e)}")
    
    def _post(
        self,
        path: str,
        data: Optional[Dict] = None,
        use_params: bool = False
    ) -> Any:
        """Make POST request."""
        url = f"{self.base_url}{path}"
        
        try:
            if use_params:
                response = self.session.post(url, params=data, timeout=self.timeout)
            else:
                response = self.session.post(url, json=data, timeout=self.timeout)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            raise VexMemoryAPIError(f"Request failed: {str(e)}")
    
    def _put(self, path: str, data: Optional[Dict] = None) -> Any:
        """Make PUT request."""
        url = f"{self.base_url}{path}"
        
        try:
            response = self.session.put(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            raise VexMemoryAPIError(f"Request failed: {str(e)}")
    
    def _delete(self, path: str) -> Any:
        """Make DELETE request."""
        url = f"{self.base_url}{path}"
        
        try:
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
            
            # DELETE may return empty response
            if response.text:
                return response.json()
            return None
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            raise VexMemoryAPIError(f"Request failed: {str(e)}")
    
    def _handle_http_error(self, error: requests.exceptions.HTTPError, response: requests.Response):
        """Handle HTTP errors uniformly."""
        try:
            error_data = response.json()
            message = error_data.get("detail", str(error))
        except (ValueError, AttributeError):
            message = str(error)
        
        raise VexMemoryAPIError(
            message=message,
            status_code=response.status_code,
            response_data=error_data if 'error_data' in locals() else None
        )
