"""
Utility functions for vex-memory SDK.
"""

from typing import Any, Dict


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.
    
    Uses simple heuristic: 1 token ≈ 4 characters.
    This is rough but sufficient for context building.
    
    Args:
        text: Text to estimate tokens for
    
    Returns:
        Estimated token count
    """
    return len(text) // 4


def truncate_to_tokens(text: str, max_tokens: int, suffix: str = "...") -> str:
    """Truncate text to fit within token limit.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum tokens allowed
        suffix: String to append if truncated
    
    Returns:
        Truncated text
    """
    current_tokens = estimate_tokens(text)
    
    if current_tokens <= max_tokens:
        return text
    
    # Calculate max characters (accounting for suffix)
    max_chars = (max_tokens * 4) - len(suffix)
    
    return text[:max_chars] + suffix


def format_memory_for_llm(memory: Any, include_metadata: bool = False) -> str:
    """Format a memory object for LLM consumption.
    
    Args:
        memory: Memory object
        include_metadata: Include memory metadata
    
    Returns:
        Formatted string
    """
    lines = [f"Content: {memory.content}"]
    
    if hasattr(memory, 'importance_score') and memory.importance_score:
        lines.append(f"Importance: {memory.importance_score:.2f}")
    
    if hasattr(memory, 'created_at') and memory.created_at:
        lines.append(f"Created: {memory.created_at}")
    
    if include_metadata and hasattr(memory, 'metadata') and memory.metadata:
        lines.append(f"Metadata: {memory.metadata}")
    
    return " | ".join(lines)


def validate_score(score: float, name: str = "score") -> None:
    """Validate a score is in valid range [0.0, 1.0].
    
    Args:
        score: Score value to validate
        name: Name of the score field (for error messages)
    
    Raises:
        ValueError: If score is out of range
    """
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0, got {score}")


def merge_metadata(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge metadata dictionaries, preserving nested structures.
    
    Args:
        base: Base metadata dict
        updates: Updates to apply
    
    Returns:
        Merged metadata dict
    """
    result = base.copy()
    
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = merge_metadata(result[key], value)
        else:
            result[key] = value
    
    return result
