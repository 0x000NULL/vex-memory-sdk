"""
CLI Configuration Management
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


DEFAULT_CONFIG = {
    "api_url": "http://localhost:8000",
    "default_namespace": None,
    "default_importance": 0.5,
    "timeout": 30,
    "output_format": "table",
    "color": True
}


class CLIConfig:
    """Manage CLI configuration file."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config manager.
        
        Args:
            config_path: Path to config file (default: ~/.vex-memory/config.json)
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".vex-memory" / "config.json"
        
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                # If config file is corrupted, use defaults
                self._config = DEFAULT_CONFIG.copy()
        else:
            # No config file, use defaults
            self._config = DEFAULT_CONFIG.copy()
        
        return self._config
    
    def save(self) -> None:
        """Save configuration to file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write config
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration.
        
        Returns:
            Full configuration dictionary
        """
        return self._config.copy()
    
    def initialize_default(self) -> None:
        """Initialize with default configuration."""
        self._config = DEFAULT_CONFIG.copy()
        self.save()
    
    def exists(self) -> bool:
        """Check if config file exists.
        
        Returns:
            True if config file exists
        """
        return self.config_path.exists()
