"""
Auto-tuning extensions for VexMemoryClient (Phase 3: Adaptive Learning)
"""

import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from .exceptions import VexMemoryAPIError, VexMemoryValidationError


class AutoTuningMixin:
    """Mixin to add auto-tuning capabilities to VexMemoryClient."""
    
    def __init__(self):
        """Initialize auto-tuning state."""
        # Auto-tuning state
        self._auto_tuning_enabled = False
        self._auto_tuning_namespace = None
        self._auto_tuning_thread = None
        self._learned_weights = None
        self._last_weight_refresh = None
        self._refresh_interval = 3600
    
    def enable_auto_tuning(
        self,
        namespace: Optional[str] = None,
        refresh_interval: int = 3600
    ):
        """Enable automatic weight optimization.
        
        When enabled, the client will periodically fetch learned weights
        from the server and use them automatically in build_context() calls.
        
        Args:
            namespace: Namespace to optimize for (if None, uses namespace from first build_context call)
            refresh_interval: Seconds between weight refreshes (default: 3600 = 1 hour)
        
        Example:
            >>> client = VexMemoryClient()
            >>> client.enable_auto_tuning(namespace="my-agent")
            >>> context = client.build_context("my query", token_budget=4000)
            # Automatically uses learned weights
        """
        self._auto_tuning_enabled = True
        self._auto_tuning_namespace = namespace
        self._refresh_interval = refresh_interval
        
        # Fetch weights immediately
        if namespace:
            try:
                weights_data = self.get_learned_weights(namespace)
                self._learned_weights = weights_data.get("weights")
                self._last_weight_refresh = datetime.utcnow()
            except VexMemoryAPIError:
                # No learned weights yet, will use defaults
                self._learned_weights = None
        
        # Start background refresh thread
        def refresh_weights():
            while self._auto_tuning_enabled:
                time.sleep(self._refresh_interval)
                if self._auto_tuning_namespace:
                    try:
                        weights_data = self.get_learned_weights(self._auto_tuning_namespace)
                        self._learned_weights = weights_data.get("weights")
                        self._last_weight_refresh = datetime.utcnow()
                    except VexMemoryAPIError:
                        # Server may not have learned weights yet
                        pass
        
        self._auto_tuning_thread = threading.Thread(target=refresh_weights, daemon=True)
        self._auto_tuning_thread.start()
    
    def disable_auto_tuning(self):
        """Disable automatic weight optimization.
        
        Stops the background refresh thread and clears learned weights.
        """
        self._auto_tuning_enabled = False
        self._learned_weights = None
        self._last_weight_refresh = None
        # Thread will exit on next iteration
    
    def get_learned_weights(self, namespace: str) -> Dict[str, Any]:
        """Get learned weights for a namespace.
        
        Args:
            namespace: Namespace to query
            
        Returns:
            Dictionary with learned weight configuration and metadata
            
        Raises:
            VexMemoryAPIError: No learned weights found or API error
        """
        return self._get(f"/api/weights/learned/{namespace}")
    
    def trigger_weight_optimization(
        self,
        namespace: str,
        search_space: Optional[Dict[str, List[float]]] = None,
        min_queries: int = 50
    ) -> Dict[str, Any]:
        """Trigger weight optimization for a namespace.
        
        This initiates a grid search over weight combinations to find
        the optimal configuration based on historical usage data.
        
        Args:
            namespace: Namespace to optimize
            search_space: Optional custom search space (dict of param -> list of values)
            min_queries: Minimum historical queries required (default: 50)
            
        Returns:
            Dictionary with optimization results including best_weights and objective_score
            
        Raises:
            VexMemoryAPIError: Optimization failed (e.g., insufficient data)
        
        Example:
            >>> client = VexMemoryClient()
            >>> result = client.trigger_weight_optimization("my-agent", min_queries=50)
            >>> print(f"Best weights: {result['best_weights']}")
            >>> print(f"Objective score: {result['objective_score']}")
        """
        payload = {
            "namespace": namespace,
            "min_queries": min_queries
        }
        
        if search_space is not None:
            payload["search_space"] = search_space
        
        return self._post("/api/weights/optimize", payload)
    
    def get_analytics_summary(self, namespace: str) -> Dict[str, Any]:
        """Get usage analytics summary for a namespace.
        
        Args:
            namespace: Namespace to query
            
        Returns:
            Dictionary with analytics summary (query count, avg tokens, efficiency, etc.)
            
        Raises:
            VexMemoryAPIError: API error
        """
        return self._get(f"/api/weights/analytics?namespace={namespace}")
    
    def export_analytics(self, namespace: str, format: str = "json") -> Any:
        """Export analytics data for a namespace.
        
        Args:
            namespace: Namespace to export
            format: Export format ("json" or "csv", default: "json")
            
        Returns:
            JSON dict (if format="json") or CSV string (if format="csv")
            
        Raises:
            VexMemoryAPIError: API error
            VexMemoryValidationError: Invalid format
        """
        if format not in ("json", "csv"):
            raise VexMemoryValidationError("Format must be 'json' or 'csv'")
        
        return self._get(f"/api/analytics/{namespace}/export?format={format}")
    
    def delete_analytics(self, namespace: str) -> Dict[str, Any]:
        """Delete all analytics data for a namespace (GDPR compliance).
        
        Args:
            namespace: Namespace to delete data for
            
        Returns:
            Dictionary with deletion confirmation
            
        Raises:
            VexMemoryAPIError: API error
        """
        return self._delete(f"/api/analytics/{namespace}")
    
    def _get_active_weights(
        self,
        user_weights: Optional[Dict[str, float]],
        namespace: Optional[str]
    ) -> Optional[Dict[str, float]]:
        """Get active weights considering user override and auto-tuning.
        
        Priority:
        1. User-provided weights (explicit override)
        2. Learned weights from auto-tuning (if enabled)
        3. None (use server defaults)
        
        Args:
            user_weights: User-provided weights (takes precedence)
            namespace: Namespace for auto-tuning
            
        Returns:
            Weights dict or None
        """
        # User override takes precedence
        if user_weights is not None:
            return user_weights
        
        # Check if auto-tuning is enabled
        if not self._auto_tuning_enabled:
            return None
        
        # Set namespace for auto-tuning if not already set
        if namespace and not self._auto_tuning_namespace:
            self._auto_tuning_namespace = namespace
            # Fetch learned weights
            try:
                weights_data = self.get_learned_weights(namespace)
                self._learned_weights = weights_data.get("weights")
                self._last_weight_refresh = datetime.utcnow()
            except VexMemoryAPIError:
                pass
        
        # Return learned weights if available
        return self._learned_weights
