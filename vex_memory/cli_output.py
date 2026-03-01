"""
CLI Output Formatting
"""

import json
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime


# Check if we're in a TTY for color support
IS_TTY = sys.stdout.isatty()


class Colors:
    """ANSI color codes for terminal output."""
    
    # Basic colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


def colorize(text: str, color: str, use_color: bool = True) -> str:
    """Apply color to text if color is enabled.
    
    Args:
        text: Text to colorize
        color: Color code from Colors class
        use_color: Whether to use color (default: True)
        
    Returns:
        Colored text if use_color is True and in TTY, otherwise plain text
    """
    if use_color and IS_TTY:
        return f"{color}{text}{Colors.RESET}"
    return text


def format_json(data: Any, pretty: bool = True) -> str:
    """Format data as JSON.
    
    Args:
        data: Data to format
        pretty: Whether to pretty-print (default: True)
        
    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, default=str)
    return json.dumps(data, default=str)


def format_memory(memory: Dict[str, Any], use_color: bool = True, show_content: bool = True) -> str:
    """Format a single memory for display.
    
    Args:
        memory: Memory dictionary
        use_color: Whether to use color
        show_content: Whether to show full content
        
    Returns:
        Formatted memory string
    """
    lines = []
    
    # Memory ID
    mem_id = memory.get('id', 'unknown')
    lines.append(colorize(f"Memory ID: {mem_id}", Colors.CYAN, use_color))
    
    # Type
    mem_type = memory.get('type', 'unknown')
    lines.append(f"Type: {colorize(mem_type, Colors.BLUE, use_color)}")
    
    # Importance
    importance = memory.get('importance_score', 0.0)
    importance_color = Colors.GREEN if importance >= 0.7 else Colors.YELLOW if importance >= 0.4 else Colors.DIM
    lines.append(f"Importance: {colorize(f'{importance:.2f}', importance_color, use_color)}")
    
    # Created at
    created = memory.get('created_at', '')
    if created:
        lines.append(f"Created: {created}")
    
    # Updated at (if different from created)
    updated = memory.get('updated_at', '')
    if updated and updated != created:
        lines.append(f"Updated: {updated}")
    
    # Namespace
    namespace = memory.get('namespace_id')
    if namespace:
        lines.append(f"Namespace: {namespace}")
    
    # Content
    if show_content:
        content = memory.get('content', '')
        lines.append(colorize("Content:", Colors.BOLD, use_color))
        # Indent content
        for line in content.split('\n'):
            lines.append(f"  {line}")
    
    # Metadata
    metadata = memory.get('metadata')
    if metadata:
        lines.append(colorize("Metadata:", Colors.BOLD, use_color))
        for key, value in metadata.items():
            lines.append(f"  {key}: {value}")
    
    return '\n'.join(lines)


def format_memory_list(
    memories: List[Dict[str, Any]],
    use_color: bool = True,
    show_content: bool = True,
    max_content_length: int = 80
) -> str:
    """Format a list of memories.
    
    Args:
        memories: List of memory dictionaries
        use_color: Whether to use color
        show_content: Whether to show content preview
        max_content_length: Maximum content preview length
        
    Returns:
        Formatted list string
    """
    if not memories:
        return colorize("No memories found.", Colors.DIM, use_color)
    
    lines = []
    for i, memory in enumerate(memories, 1):
        mem_id = memory.get('id', 'unknown')[:12] + '...'
        created = memory.get('created_at') or ''
        created = created[:10] if created else 'unknown'  # Just the date
        importance = memory.get('importance_score', 0.0)
        
        # Format header line
        importance_color = Colors.GREEN if importance >= 0.7 else Colors.YELLOW if importance >= 0.4 else Colors.DIM
        header = f"[{colorize(mem_id, Colors.CYAN, use_color)}] "
        header += f"({created}) "
        header += f"Importance: {colorize(f'{importance:.2f}', importance_color, use_color)}"
        
        lines.append(header)
        
        # Show content preview if requested
        if show_content:
            content = memory.get('content', '')
            if len(content) > max_content_length:
                content = content[:max_content_length] + '...'
            # Replace newlines with spaces for preview
            content = content.replace('\n', ' ')
            lines.append(f"  {content}")
        
        # Add blank line between memories
        if i < len(memories):
            lines.append("")
    
    return '\n'.join(lines)


def format_search_results(
    results: List[Dict[str, Any]],
    use_color: bool = True,
    max_content_length: int = 120
) -> str:
    """Format search results with similarity scores.
    
    Args:
        results: List of memory dictionaries (may include similarity/score fields)
        use_color: Whether to use color
        max_content_length: Maximum content preview length
        
    Returns:
        Formatted search results string
    """
    if not results:
        return colorize("No results found.", Colors.DIM, use_color)
    
    lines = [colorize(f"Found {len(results)} result(s):\n", Colors.BOLD, use_color)]
    
    for i, memory in enumerate(results, 1):
        # Handle both {"memory": {...}, "similarity": ...} and plain memory objects
        if 'memory' in memory:
            actual_memory = memory['memory']
            similarity = memory.get('similarity', 0.0)
        else:
            actual_memory = memory
            similarity = memory.get('similarity', memory.get('score', 0.0))
        
        importance = actual_memory.get('importance_score', 0.0)
        
        # Format similarity score
        sim_color = Colors.GREEN if similarity >= 0.8 else Colors.YELLOW if similarity >= 0.6 else Colors.WHITE
        
        # Header line
        header = f"[{i}] "
        if similarity > 0:
            header += f"(similarity: {colorize(f'{similarity:.2f}', sim_color, use_color)}, "
        header += f"importance: {colorize(f'{importance:.2f}', Colors.BLUE, use_color)})"
        lines.append(header)
        
        # Content preview
        content = actual_memory.get('content', '')
        if len(content) > max_content_length:
            content = content[:max_content_length] + '...'
        content = content.replace('\n', ' ')
        lines.append(f"    {content}")
        
        # Created date
        created_at = actual_memory.get('created_at')
        if created_at:
            created = created_at[:10] if created_at else ''
            if created:
                lines.append(colorize(f"    Created: {created}", Colors.DIM, use_color))
        
        lines.append("")  # Blank line
    
    return '\n'.join(lines)


def format_context_result(
    result: Dict[str, Any],
    use_color: bool = True
) -> str:
    """Format context building result.
    
    Args:
        result: Context result dictionary
        use_color: Whether to use color
        
    Returns:
        Formatted context string
    """
    memories = result.get('memories', [])
    metadata = result.get('metadata', {})
    
    # Header
    token_count = metadata.get('total_tokens', 0)
    budget = metadata.get('token_budget', 0)
    utilization = (token_count / budget * 100) if budget > 0 else 0
    
    header = colorize(
        f"Context ({len(memories)} memories, {token_count} tokens, {utilization:.1f}% utilization):\n",
        Colors.BOLD,
        use_color
    )
    
    lines = [header]
    
    # Show each memory
    for memory in memories:
        created = memory.get('created_at', '')[:10]
        score = memory.get('composite_score', memory.get('score', 0.0))
        content = memory.get('content', '')
        
        # Limit content display
        if len(content) > 200:
            content = content[:200] + '...'
        
        score_color = Colors.GREEN if score >= 0.7 else Colors.YELLOW if score >= 0.5 else Colors.WHITE
        
        lines.append(f"[{colorize(created, Colors.CYAN, use_color)}] "
                    f"(score: {colorize(f'{score:.2f}', score_color, use_color)})")
        lines.append(f"  {content}\n")
    
    return '\n'.join(lines)


def format_stats(stats: Dict[str, Any], use_color: bool = True) -> str:
    """Format statistics for display.
    
    Args:
        stats: Statistics dictionary
        use_color: Whether to use color
        
    Returns:
        Formatted statistics string
    """
    lines = [colorize("Memory Statistics:", Colors.BOLD, use_color)]
    
    # Total memories
    total = stats.get('total_memories', 0)
    lines.append(f"  Total memories: {colorize(str(total), Colors.CYAN, use_color)}")
    
    # By type
    by_type = stats.get('by_type', {})
    if by_type:
        lines.append("\n  By type:")
        for mem_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"    {mem_type}: {count} ({percentage:.1f}%)")
    
    # By importance
    by_importance = stats.get('by_importance', {})
    if by_importance:
        lines.append("\n  By importance:")
        for category, count in by_importance.items():
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"    {category}: {count} ({percentage:.1f}%)")
    
    # Namespaces
    namespace_count = stats.get('namespace_count', 0)
    if namespace_count:
        lines.append(f"\n  Namespaces: {namespace_count}")
    
    # Average importance
    avg_importance = stats.get('average_importance', 0.0)
    if avg_importance:
        lines.append(f"  Average importance: {avg_importance:.2f}")
    
    return '\n'.join(lines)


def format_error(message: str, use_color: bool = True) -> str:
    """Format error message.
    
    Args:
        message: Error message
        use_color: Whether to use color
        
    Returns:
        Formatted error string
    """
    return colorize(f"Error: {message}", Colors.RED, use_color)


def format_success(message: str, use_color: bool = True) -> str:
    """Format success message.
    
    Args:
        message: Success message
        use_color: Whether to use color
        
    Returns:
        Formatted success string
    """
    return colorize(message, Colors.GREEN, use_color)


def format_warning(message: str, use_color: bool = True) -> str:
    """Format warning message.
    
    Args:
        message: Warning message
        use_color: Whether to use color
        
    Returns:
        Formatted warning string
    """
    return colorize(f"Warning: {message}", Colors.YELLOW, use_color)
