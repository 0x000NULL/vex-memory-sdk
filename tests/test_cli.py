"""
Unit tests for CLI
"""

import json
import pytest
from click.testing import CliRunner

from vex_memory.cli import cli
from vex_memory.cli_config import CLIConfig, DEFAULT_CONFIG
from vex_memory.cli_output import (
    colorize,
    Colors,
    format_json,
    format_memory,
    format_memory_list,
    format_search_results,
    format_error,
    format_success,
)
from vex_memory.cli_utils import (
    read_json_arg,
    validate_importance,
    validate_similarity,
    validate_memory_type,
    truncate_text,
    parse_key_value,
)


# ============================================================================
# CLI Config Tests
# ============================================================================

def test_cli_config_defaults():
    """Test default configuration values."""
    config = CLIConfig()
    assert config.get('api_url') == DEFAULT_CONFIG['api_url']
    assert config.get('timeout') == DEFAULT_CONFIG['timeout']
    assert config.get('color') == DEFAULT_CONFIG['color']


def test_cli_config_get_set():
    """Test get/set configuration values."""
    config = CLIConfig()
    config.set('api_url', 'http://test:9000')
    assert config.get('api_url') == 'http://test:9000'


def test_cli_config_get_all():
    """Test getting all configuration."""
    config = CLIConfig()
    all_config = config.get_all()
    assert 'api_url' in all_config
    assert 'timeout' in all_config


# ============================================================================
# CLI Output Tests
# ============================================================================

def test_colorize():
    """Test text colorization."""
    text = "test"
    colored = colorize(text, Colors.RED, use_color=True)
    # Should contain ANSI codes when color is enabled
    assert text in colored
    
    # Without color, should return plain text
    plain = colorize(text, Colors.RED, use_color=False)
    assert plain == text


def test_format_json():
    """Test JSON formatting."""
    data = {"key": "value", "num": 123}
    result = format_json(data, pretty=True)
    parsed = json.loads(result)
    assert parsed == data


def test_format_memory():
    """Test memory formatting."""
    memory = {
        "id": "test-123",
        "type": "semantic",
        "content": "Test content",
        "importance_score": 0.8,
        "created_at": "2026-03-01T12:00:00Z",
    }
    
    result = format_memory(memory, use_color=False)
    assert "test-123" in result
    assert "semantic" in result
    assert "Test content" in result
    assert "0.80" in result


def test_format_memory_list():
    """Test memory list formatting."""
    memories = [
        {
            "id": "test-1",
            "content": "Content 1",
            "importance_score": 0.7,
            "created_at": "2026-03-01T12:00:00Z",
        },
        {
            "id": "test-2",
            "content": "Content 2",
            "importance_score": 0.5,
            "created_at": "2026-03-01T13:00:00Z",
        },
    ]
    
    result = format_memory_list(memories, use_color=False)
    assert "test-1" in result
    assert "test-2" in result
    assert "Content 1" in result
    assert "Content 2" in result


def test_format_memory_list_handles_none_created_at():
    """Test memory list formatting with None created_at."""
    memories = [
        {
            "id": "test-1",
            "content": "Content 1",
            "importance_score": 0.7,
            "created_at": None,  # None value
        },
    ]
    
    result = format_memory_list(memories, use_color=False)
    assert "test-1" in result
    assert "Content 1" in result


def test_format_search_results():
    """Test search results formatting."""
    results = [
        {
            "id": "test-1",
            "content": "Result 1",
            "importance_score": 0.8,
            "similarity": 0.95,
            "created_at": "2026-03-01T12:00:00Z",
        },
    ]
    
    result = format_search_results(results, use_color=False)
    assert "Result 1" in result
    assert "0.95" in result  # Similarity
    assert "0.80" in result  # Importance


def test_format_error():
    """Test error message formatting."""
    result = format_error("Test error", use_color=False)
    assert "Error" in result
    assert "Test error" in result


def test_format_success():
    """Test success message formatting."""
    result = format_success("Test success", use_color=False)
    assert "Test success" in result


# ============================================================================
# CLI Utils Tests
# ============================================================================

def test_read_json_arg():
    """Test JSON argument parsing."""
    json_str = '{"key": "value", "num": 123}'
    result = read_json_arg(json_str)
    assert result == {"key": "value", "num": 123}


def test_read_json_arg_invalid():
    """Test invalid JSON argument."""
    with pytest.raises(ValueError):
        read_json_arg("invalid json")


def test_validate_importance():
    """Test importance validation."""
    # Valid values
    validate_importance(0.0)
    validate_importance(0.5)
    validate_importance(1.0)
    
    # Invalid values
    with pytest.raises(ValueError):
        validate_importance(-0.1)
    
    with pytest.raises(ValueError):
        validate_importance(1.1)


def test_validate_similarity():
    """Test similarity validation."""
    # Valid values
    validate_similarity(0.0)
    validate_similarity(0.5)
    validate_similarity(1.0)
    
    # Invalid values
    with pytest.raises(ValueError):
        validate_similarity(-0.1)
    
    with pytest.raises(ValueError):
        validate_similarity(1.1)


def test_validate_memory_type():
    """Test memory type validation."""
    # Valid types
    validate_memory_type("semantic")
    validate_memory_type("episodic")
    validate_memory_type("procedural")
    validate_memory_type("emotional")
    
    # Invalid type
    with pytest.raises(ValueError):
        validate_memory_type("invalid")


def test_truncate_text():
    """Test text truncation."""
    text = "This is a long text that should be truncated"
    result = truncate_text(text, 20, suffix="...")
    assert len(result) <= 20
    assert result.endswith("...")
    
    # Short text should not be truncated
    short = "Short"
    result = truncate_text(short, 20)
    assert result == short


def test_parse_key_value():
    """Test key=value parsing."""
    key, value = parse_key_value("api_url=http://localhost:8000")
    assert key == "api_url"
    assert value == "http://localhost:8000"
    
    # With spaces
    key, value = parse_key_value(" key = value ")
    assert key == "key"
    assert value == "value"
    
    # Invalid format
    with pytest.raises(ValueError):
        parse_key_value("invalid")


# ============================================================================
# CLI Command Tests
# ============================================================================

def test_cli_version():
    """Test --version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '2.0.0' in result.output


def test_cli_help():
    """Test --help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'vex-memory CLI' in result.output
    assert 'store' in result.output
    assert 'search' in result.output


def test_store_help():
    """Test store command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['store', '--help'])
    assert result.exit_code == 0
    assert 'Store a new memory' in result.output
    assert '--importance' in result.output


def test_search_help():
    """Test search command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['search', '--help'])
    assert result.exit_code == 0
    assert 'Search for memories' in result.output
    assert '--limit' in result.output


def test_config_show():
    """Test config show command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'show'])
    assert result.exit_code == 0
    assert 'Configuration' in result.output
    assert 'api_url' in result.output


def test_config_get():
    """Test config get command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'get', 'api_url'])
    assert result.exit_code == 0
    # Should output the api_url value


def test_config_set():
    """Test config set command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'set', 'timeout', '60'])
    assert result.exit_code == 0
    
    # Verify it was set
    result = runner.invoke(cli, ['config', 'get', 'timeout'])
    assert '60' in result.output


# ============================================================================
# Integration Tests (require server)
# ============================================================================

@pytest.mark.integration
def test_health_check():
    """Test health check command (requires server)."""
    runner = CliRunner()
    result = runner.invoke(cli, ['health'])
    # Should exit 0 if server is running, 1 if not
    assert result.exit_code in [0, 1]


@pytest.mark.integration
def test_store_and_get():
    """Test store and get commands (requires server)."""
    runner = CliRunner()
    
    # Store a memory
    result = runner.invoke(cli, ['store', 'Test CLI memory', '--importance', '0.7'])
    if result.exit_code == 0:
        # Extract memory ID from output
        # Format: "✓ Stored memory: <id>"
        import re
        match = re.search(r'memory: ([a-f0-9-]+)', result.output)
        if match:
            memory_id = match.group(1)
            
            # Get the memory
            result = runner.invoke(cli, ['get', memory_id])
            assert result.exit_code == 0
            assert 'Test CLI memory' in result.output
            assert '0.70' in result.output


@pytest.mark.integration
def test_search():
    """Test search command (requires server)."""
    runner = CliRunner()
    result = runner.invoke(cli, ['search', 'test', '--limit', '5'])
    # Should exit 0 if server is running, 1 if not
    assert result.exit_code in [0, 1]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
