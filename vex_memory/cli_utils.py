"""
CLI Utility Functions
"""

import sys
import json
from typing import Any, Dict, Optional


def read_json_arg(json_str: str) -> Dict[str, Any]:
    """Parse JSON string argument.
    
    Args:
        json_str: JSON string
        
    Returns:
        Parsed dictionary
        
    Raises:
        ValueError: If JSON is invalid
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def read_file(file_path: str) -> str:
    """Read content from file.
    
    Args:
        file_path: Path to file
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file can't be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}")


def confirm(message: str, default: bool = False) -> bool:
    """Prompt user for yes/no confirmation.
    
    Args:
        message: Confirmation message
        default: Default value if user just presses Enter
        
    Returns:
        True if user confirms, False otherwise
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    
    while True:
        try:
            response = input(message + suffix).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()  # New line after ^C
            return False
        
        if not response:
            return default
        
        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        else:
            print("Please respond with 'y' or 'n'")


def validate_importance(importance: float) -> None:
    """Validate importance score.
    
    Args:
        importance: Importance score
        
    Raises:
        ValueError: If importance is out of range
    """
    if not 0.0 <= importance <= 1.0:
        raise ValueError("Importance must be between 0.0 and 1.0")


def validate_similarity(similarity: float) -> None:
    """Validate similarity score.
    
    Args:
        similarity: Similarity score
        
    Raises:
        ValueError: If similarity is out of range
    """
    if not 0.0 <= similarity <= 1.0:
        raise ValueError("Similarity must be between 0.0 and 1.0")


def validate_memory_type(memory_type: str) -> None:
    """Validate memory type.
    
    Args:
        memory_type: Memory type string
        
    Raises:
        ValueError: If memory type is invalid
    """
    valid_types = ['semantic', 'episodic', 'procedural', 'emotional']
    if memory_type not in valid_types:
        raise ValueError(
            f"Invalid memory type '{memory_type}'. "
            f"Must be one of: {', '.join(valid_types)}"
        )


def format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp for display.
    
    Args:
        timestamp: ISO format timestamp string
        
    Returns:
        Formatted timestamp string
    """
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, AttributeError):
        return timestamp


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated (default: '...')
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_key_value(kv_str: str) -> tuple[str, str]:
    """Parse key=value string.
    
    Args:
        kv_str: Key=value string
        
    Returns:
        Tuple of (key, value)
        
    Raises:
        ValueError: If format is invalid
    """
    parts = kv_str.split('=', 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid key=value format: {kv_str}")
    return parts[0].strip(), parts[1].strip()


def verbose_print(message: str, verbose: bool = False) -> None:
    """Print message only if verbose mode is enabled.
    
    Args:
        message: Message to print
        verbose: Whether verbose mode is enabled
    """
    if verbose:
        print(f"[VERBOSE] {message}", file=sys.stderr)


def get_terminal_width() -> int:
    """Get terminal width.
    
    Returns:
        Terminal width in columns (default: 80)
    """
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except Exception:
        return 80
