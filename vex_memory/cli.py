"""
vex-memory CLI - Command-line interface for vex-memory SDK
"""

import sys
import json
import click
from typing import Optional, Dict, Any

from .client import VexMemoryClient
from .exceptions import VexMemoryError, VexMemoryAPIError, VexMemoryValidationError
from .cli_config import CLIConfig
from .cli_output import (
    format_json,
    format_memory,
    format_memory_list,
    format_search_results,
    format_context_result,
    format_stats,
    format_error,
    format_success,
    format_warning,
)
from .cli_utils import (
    read_json_arg,
    read_file,
    confirm,
    validate_importance,
    validate_similarity,
    validate_memory_type,
    verbose_print,
)

__version__ = "2.0.0"


# Global context object for passing between commands
class Context:
    """CLI context object."""
    
    def __init__(self):
        self.client: Optional[VexMemoryClient] = None
        self.config: Optional[CLIConfig] = None
        self.verbose: bool = False
        self.json_output: bool = False
        self.use_color: bool = True


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.option('--base-url', '-u', envvar='VEX_MEMORY_URL', 
              help='vex-memory API base URL')
@click.option('--timeout', '-T', type=int, 
              help='Request timeout in seconds')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose output')
@click.option('--json', 'json_output', is_flag=True, 
              help='Output as JSON')
@click.option('--no-color', is_flag=True, 
              help='Disable colored output')
@click.version_option(version=__version__, prog_name='vex-memory')
@pass_context
def cli(ctx: Context, base_url: Optional[str], timeout: Optional[int], 
        verbose: bool, json_output: bool, no_color: bool):
    """vex-memory CLI - Intelligent memory management for AI agents."""
    
    # Initialize config
    ctx.config = CLIConfig()
    ctx.verbose = verbose
    ctx.json_output = json_output
    ctx.use_color = not no_color
    
    # Get base URL from CLI arg, config, or default
    if not base_url:
        base_url = ctx.config.get('api_url', 'http://localhost:8000')
    
    # Get timeout from CLI arg, config, or default
    if not timeout:
        timeout = ctx.config.get('timeout', 30)
    
    verbose_print(f"Connecting to {base_url}", verbose)
    
    # Initialize client
    try:
        ctx.client = VexMemoryClient(base_url=base_url, timeout=timeout)
    except Exception as e:
        click.echo(format_error(f"Failed to initialize client: {e}", ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# STORE COMMAND
# ============================================================================

@cli.command()
@click.argument('content', required=False)
@click.option('--importance', '-i', type=float, default=0.5,
              help='Importance score (0.0-1.0)')
@click.option('--type', '-t', 'memory_type', default='semantic',
              type=click.Choice(['semantic', 'episodic', 'procedural', 'emotional']),
              help='Memory type')
@click.option('--namespace', '-n', help='Namespace ID')
@click.option('--metadata', '-m', help='JSON metadata string')
@click.option('--file', '-f', 'file_path', help='Read content from file')
@pass_context
def store(ctx: Context, content: Optional[str], importance: float, 
          memory_type: str, namespace: Optional[str], metadata: Optional[str],
          file_path: Optional[str]):
    """Store a new memory.
    
    Examples:
    
        vex-memory store "Project deadline is March 15th"
        
        vex-memory store "Meeting notes" --importance 0.9 --type episodic
        
        vex-memory store --file notes.txt --metadata '{"project":"vex"}'
    """
    
    # Get content from file or argument
    if file_path:
        try:
            content = read_file(file_path)
            verbose_print(f"Read {len(content)} characters from {file_path}", ctx.verbose)
        except Exception as e:
            click.echo(format_error(str(e), ctx.use_color), err=True)
            sys.exit(1)
    
    if not content:
        click.echo(format_error("Content is required (provide as argument or --file)", ctx.use_color), err=True)
        sys.exit(1)
    
    # Validate importance
    try:
        validate_importance(importance)
    except ValueError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)
    
    # Parse metadata if provided
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = read_json_arg(metadata)
        except ValueError as e:
            click.echo(format_error(str(e), ctx.use_color), err=True)
            sys.exit(1)
    
    # Use default namespace from config if not provided
    if not namespace:
        namespace = ctx.config.get('default_namespace')
    
    # Store memory
    try:
        verbose_print(f"Storing memory (type={memory_type}, importance={importance})", ctx.verbose)
        result = ctx.client.store_memory(
            content=content,
            importance_score=importance,
            memory_type=memory_type,
            namespace_id=namespace,
            metadata=metadata_dict
        )
        
        if ctx.json_output:
            click.echo(format_json(result))
        else:
            click.echo(format_success(f"✓ Stored memory: {result['id']}", ctx.use_color))
            click.echo(f"  Type: {result.get('type', 'unknown')}")
            click.echo(f"  Importance: {result.get('importance_score', 0.0):.2f}")
            
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# SEARCH COMMAND
# ============================================================================

@cli.command()
@click.argument('query')
@click.option('--limit', '-l', type=int, default=10,
              help='Maximum number of results')
@click.option('--min-similarity', type=float, default=0.5,
              help='Minimum similarity score (0.0-1.0)')
@click.option('--type', '-t', 'memory_type',
              type=click.Choice(['semantic', 'episodic', 'procedural', 'emotional']),
              help='Filter by memory type')
@click.option('--namespace', '-n', help='Filter by namespace')
@click.option('--min-importance', type=float,
              help='Filter by minimum importance')
@pass_context
def search(ctx: Context, query: str, limit: int, min_similarity: float,
           memory_type: Optional[str], namespace: Optional[str],
           min_importance: Optional[float]):
    """Search for memories.
    
    Examples:
    
        vex-memory search "project deadline"
        
        vex-memory search "meeting" --limit 20 --min-similarity 0.7
        
        vex-memory search "notes" --type episodic --namespace work
    """
    
    # Validate similarity
    try:
        validate_similarity(min_similarity)
    except ValueError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)
    
    # Use default namespace from config if not provided
    if not namespace:
        namespace = ctx.config.get('default_namespace')
    
    # Search
    try:
        verbose_print(f"Searching for '{query}' (limit={limit})", ctx.verbose)
        results = ctx.client.search_memories(
            query=query,
            limit=limit,
            min_similarity=min_similarity,
            memory_type=memory_type,
            namespace_id=namespace
        )
        
        if ctx.json_output:
            click.echo(format_json(results))
        else:
            # Filter by min_importance if specified (client-side for now)
            if min_importance is not None:
                results = [
                    r for r in results 
                    if r.get('memory', {}).get('importance_score', 0.0) >= min_importance
                ]
            
            click.echo(format_search_results(results, ctx.use_color))
            
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# GET COMMAND
# ============================================================================

@cli.command()
@click.argument('memory_id')
@pass_context
def get(ctx: Context, memory_id: str):
    """Get a memory by ID.
    
    Examples:
    
        vex-memory get abc123-def456-789...
    """
    
    try:
        verbose_print(f"Fetching memory {memory_id}", ctx.verbose)
        memory = ctx.client.get_memory(memory_id)
        
        if ctx.json_output:
            click.echo(format_json(memory))
        else:
            click.echo(format_memory(memory, ctx.use_color))
            
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# LIST COMMAND
# ============================================================================

@cli.command()
@click.option('--limit', '-l', type=int, default=10,
              help='Maximum number of memories')
@click.option('--offset', type=int, default=0,
              help='Skip first N memories (pagination)')
@click.option('--type', '-t', 'memory_type',
              type=click.Choice(['semantic', 'episodic', 'procedural', 'emotional']),
              help='Filter by memory type')
@click.option('--namespace', '-n', help='Filter by namespace')
@click.option('--min-importance', type=float,
              help='Filter by minimum importance')
@pass_context
def list(ctx: Context, limit: int, offset: int, memory_type: Optional[str],
         namespace: Optional[str], min_importance: Optional[float]):
    """List recent memories.
    
    Examples:
    
        vex-memory list
        
        vex-memory list --limit 50 --type episodic
        
        vex-memory list --namespace work --min-importance 0.7
    """
    
    # Use default namespace from config if not provided
    if not namespace:
        namespace = ctx.config.get('default_namespace')
    
    try:
        verbose_print(f"Listing memories (limit={limit}, offset={offset})", ctx.verbose)
        memories = ctx.client.list_memories(
            limit=limit,
            offset=offset,
            memory_type=memory_type,
            namespace_id=namespace
        )
        
        # Filter by min_importance if specified (client-side)
        if min_importance is not None:
            memories = [
                m for m in memories 
                if m.get('importance_score', 0.0) >= min_importance
            ]
        
        if ctx.json_output:
            click.echo(format_json(memories))
        else:
            if memories:
                click.echo(f"Showing {len(memories)} memories:\n")
                click.echo(format_memory_list(memories, ctx.use_color))
            else:
                click.echo(format_warning("No memories found.", ctx.use_color))
            
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# UPDATE COMMAND
# ============================================================================

@cli.command()
@click.argument('memory_id')
@click.option('--content', '-c', help='New content')
@click.option('--importance', '-i', type=float, help='New importance score')
@click.option('--metadata', '-m', help='New metadata (JSON)')
@pass_context
def update(ctx: Context, memory_id: str, content: Optional[str],
           importance: Optional[float], metadata: Optional[str]):
    """Update a memory.
    
    Examples:
    
        vex-memory update abc123... --importance 0.9
        
        vex-memory update abc123... --content "Updated content"
        
        vex-memory update abc123... --metadata '{"reviewed":true}'
    """
    
    if not any([content, importance is not None, metadata]):
        click.echo(format_error("At least one of --content, --importance, or --metadata is required", ctx.use_color), err=True)
        sys.exit(1)
    
    # Validate importance if provided
    if importance is not None:
        try:
            validate_importance(importance)
        except ValueError as e:
            click.echo(format_error(str(e), ctx.use_color), err=True)
            sys.exit(1)
    
    # Parse metadata if provided
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = read_json_arg(metadata)
        except ValueError as e:
            click.echo(format_error(str(e), ctx.use_color), err=True)
            sys.exit(1)
    
    try:
        verbose_print(f"Updating memory {memory_id}", ctx.verbose)
        result = ctx.client.update_memory(
            memory_id=memory_id,
            content=content,
            importance_score=importance,
            metadata=metadata_dict
        )
        
        if ctx.json_output:
            click.echo(format_json(result))
        else:
            click.echo(format_success(f"✓ Updated memory {memory_id}", ctx.use_color))
            if importance is not None:
                click.echo(f"  Importance: {importance:.2f}")
            if content:
                click.echo(f"  Content updated")
            if metadata_dict:
                click.echo(f"  Metadata updated")
            
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# DELETE COMMAND
# ============================================================================

@cli.command()
@click.argument('memory_id')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@pass_context
def delete(ctx: Context, memory_id: str, yes: bool):
    """Delete a memory.
    
    Examples:
    
        vex-memory delete abc123...
        
        vex-memory delete abc123... --yes  # Skip confirmation
    """
    
    # Get memory for confirmation (unless --yes)
    if not yes:
        try:
            memory = ctx.client.get_memory(memory_id)
            content_preview = memory.get('content', '')[:50]
            if len(memory.get('content', '')) > 50:
                content_preview += '...'
            
            if not confirm(f"Delete memory {memory_id[:12]}... \"{content_preview}\"?"):
                click.echo("Cancelled.")
                return
        except VexMemoryError as e:
            # If we can't fetch the memory, still confirm with just ID
            if not confirm(f"Delete memory {memory_id}?"):
                click.echo("Cancelled.")
                return
    
    try:
        verbose_print(f"Deleting memory {memory_id}", ctx.verbose)
        ctx.client.delete_memory(memory_id)
        
        if ctx.json_output:
            click.echo(format_json({"status": "deleted", "id": memory_id}))
        else:
            click.echo(format_success(f"✓ Deleted memory {memory_id}", ctx.use_color))
            
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# CONTEXT COMMAND
# ============================================================================

@cli.command()
@click.argument('query')
@click.option('--token-budget', '-b', type=int, default=4000,
              help='Token budget')
@click.option('--model', '-m', default='gpt-4',
              help='LLM model for token counting')
@click.option('--use-mmr', is_flag=True,
              help='Use Maximal Marginal Relevance')
@click.option('--mmr-lambda', type=float, default=0.7,
              help='MMR lambda (0=diversity, 1=relevance)')
@click.option('--diversity', '-d', 'diversity_threshold', type=float, default=0.7,
              help='Diversity threshold (0.0-1.0)')
@click.option('--min-score', type=float,
              help='Minimum composite score')
@click.option('--namespace', '-n', help='Filter by namespace')
@pass_context
def context(ctx: Context, query: str, token_budget: int, model: str,
            use_mmr: bool, mmr_lambda: float, diversity_threshold: float,
            min_score: Optional[float], namespace: Optional[str]):
    """Build intelligent context.
    
    Examples:
    
        vex-memory context "recent work"
        
        vex-memory context "project" --token-budget 4000 --use-mmr
        
        vex-memory context "meeting" --diversity 0.6 --namespace work
    """
    
    # Use default namespace from config if not provided
    if not namespace:
        namespace = ctx.config.get('default_namespace')
    
    try:
        verbose_print(f"Building context for '{query}' (budget={token_budget})", ctx.verbose)
        result = ctx.client.build_context(
            query=query,
            token_budget=token_budget,
            model=model,
            use_mmr=use_mmr,
            mmr_lambda=mmr_lambda,
            diversity_threshold=diversity_threshold,
            min_score=min_score,
            namespace=namespace
        )
        
        if ctx.json_output:
            click.echo(format_json(result))
        else:
            click.echo(format_context_result(result, ctx.use_color))
            
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# HEALTH COMMAND
# ============================================================================

@cli.command()
@pass_context
def health(ctx: Context):
    """Check server health.
    
    Examples:
    
        vex-memory health
    """
    
    try:
        verbose_print("Checking server health", ctx.verbose)
        health_data = ctx.client.health_check()
        
        if ctx.json_output:
            click.echo(format_json(health_data))
        else:
            status = health_data.get('status', 'unknown')
            
            if status == 'healthy':
                click.echo(format_success(f"Server: {ctx.client.base_url}", ctx.use_color))
                click.echo(format_success("Status: OK ✓", ctx.use_color))
            else:
                click.echo(f"Server: {ctx.client.base_url}")
                click.echo(format_warning(f"Status: {status}", ctx.use_color))
            
            # Show additional details if available
            if 'database' in health_data:
                db_status = health_data['database']
                if db_status == 'connected':
                    click.echo(format_success("Database: Connected ✓", ctx.use_color))
                else:
                    click.echo(format_warning(f"Database: {db_status}", ctx.use_color))
            
            if 'memory_count' in health_data:
                click.echo(f"Memories: {health_data['memory_count']:,}")
            
            if 'uptime' in health_data:
                click.echo(f"Uptime: {health_data['uptime']}")
                
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# STATS COMMAND
# ============================================================================

@cli.command()
@click.option('--namespace', '-n', help='Stats for specific namespace')
@pass_context
def stats(ctx: Context, namespace: Optional[str]):
    """Show memory statistics.
    
    Examples:
    
        vex-memory stats
        
        vex-memory stats --namespace work
    """
    
    # Use default namespace from config if not provided
    if not namespace:
        namespace = ctx.config.get('default_namespace')
    
    try:
        verbose_print("Fetching statistics", ctx.verbose)
        stats_data = ctx.client.get_stats(namespace_id=namespace)
        
        if ctx.json_output:
            click.echo(format_json(stats_data))
        else:
            click.echo(format_stats(stats_data, ctx.use_color))
            
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# CONFIG COMMANDS
# ============================================================================

@cli.group()
def config():
    """Manage configuration.
    
    Examples:
    
        vex-memory config show
        
        vex-memory config init
        
        vex-memory config set api_url http://localhost:8000
    """
    pass


@config.command('show')
@pass_context
def config_show(ctx: Context):
    """Display current configuration."""
    
    config_data = ctx.config.get_all()
    config_path = ctx.config.config_path
    
    if ctx.json_output:
        click.echo(format_json(config_data))
    else:
        click.echo(f"Configuration ({config_path}):")
        for key, value in config_data.items():
            click.echo(f"  {key}: {value}")


@config.command('init')
@pass_context
def config_init(ctx: Context):
    """Initialize default configuration file."""
    
    if ctx.config.exists():
        if not confirm(f"Config file already exists at {ctx.config.config_path}. Overwrite?"):
            click.echo("Cancelled.")
            return
    
    ctx.config.initialize_default()
    
    if ctx.json_output:
        click.echo(format_json({"status": "initialized", "path": str(ctx.config.config_path)}))
    else:
        click.echo(format_success(f"✓ Initialized config at {ctx.config.config_path}", ctx.use_color))


@config.command('get')
@click.argument('key')
@pass_context
def config_get(ctx: Context, key: str):
    """Get configuration value."""
    
    value = ctx.config.get(key)
    
    if ctx.json_output:
        click.echo(format_json({key: value}))
    else:
        if value is not None:
            click.echo(f"{key}: {value}")
        else:
            click.echo(format_warning(f"Key '{key}' not found in config", ctx.use_color))


@config.command('set')
@click.argument('key')
@click.argument('value')
@pass_context
def config_set(ctx: Context, key: str, value: str):
    """Set configuration value."""
    
    # Try to parse as JSON value (for booleans, numbers, null)
    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        # Keep as string
        parsed_value = value
    
    ctx.config.set(key, parsed_value)
    ctx.config.save()
    
    if ctx.json_output:
        click.echo(format_json({"status": "updated", "key": key, "value": parsed_value}))
    else:
        click.echo(format_success(f"✓ Set {key} = {parsed_value}", ctx.use_color))


# ============================================================================
# NAMESPACE COMMANDS
# ============================================================================

@cli.group()
def namespace():
    """Manage namespaces.
    
    Examples:
    
        vex-memory namespace list
        
        vex-memory namespace create "work" --owner my-agent
    """
    pass


@namespace.command('create')
@click.argument('name')
@click.option('--owner', help='Owner agent ID')
@pass_context
def namespace_create(ctx: Context, name: str, owner: Optional[str]):
    """Create a new namespace."""
    
    try:
        verbose_print(f"Creating namespace '{name}'", ctx.verbose)
        result = ctx.client.create_namespace(name=name, owner_id=owner)
        
        if ctx.json_output:
            click.echo(format_json(result))
        else:
            click.echo(format_success(f"✓ Created namespace: {result.get('id', 'unknown')}", ctx.use_color))
            click.echo(f"  Name: {name}")
            if owner:
                click.echo(f"  Owner: {owner}")
                
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


@namespace.command('list')
@pass_context
def namespace_list(ctx: Context):
    """List all namespaces."""
    
    try:
        verbose_print("Listing namespaces", ctx.verbose)
        namespaces = ctx.client.list_namespaces()
        
        if ctx.json_output:
            click.echo(format_json(namespaces))
        else:
            if namespaces:
                click.echo(f"Found {len(namespaces)} namespace(s):\n")
                for ns in namespaces:
                    click.echo(f"  [{ns.get('id', 'unknown')[:12]}...] {ns.get('name', 'unnamed')}")
                    if 'owner_id' in ns:
                        click.echo(f"    Owner: {ns['owner_id']}")
            else:
                click.echo(format_warning("No namespaces found.", ctx.use_color))
                
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


@namespace.command('delete')
@click.argument('namespace_id')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@pass_context
def namespace_delete(ctx: Context, namespace_id: str, yes: bool):
    """Delete a namespace."""
    
    if not yes:
        if not confirm(f"Delete namespace {namespace_id}? This will delete all memories in this namespace."):
            click.echo("Cancelled.")
            return
    
    try:
        verbose_print(f"Deleting namespace {namespace_id}", ctx.verbose)
        ctx.client.delete_namespace(namespace_id)
        
        if ctx.json_output:
            click.echo(format_json({"status": "deleted", "id": namespace_id}))
        else:
            click.echo(format_success(f"✓ Deleted namespace {namespace_id}", ctx.use_color))
            
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# WEIGHTS COMMANDS
# ============================================================================

@cli.group()
def weights():
    """Manage context building weights.
    
    Examples:
    
        vex-memory weights presets
        
        vex-memory weights recommend balanced
    """
    pass


@weights.command('presets')
@pass_context
def weights_presets(ctx: Context):
    """List available weight presets."""
    
    try:
        verbose_print("Fetching weight presets", ctx.verbose)
        presets = ctx.client.get_weight_presets()
        
        if ctx.json_output:
            click.echo(format_json(presets))
        else:
            click.echo("Available weight presets:\n")
            for name, weights in presets.items():
                click.echo(f"  {name}:")
                for key, value in weights.items():
                    click.echo(f"    {key}: {value}")
                click.echo()
                
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


@weights.command('recommend')
@click.argument('preset_name')
@pass_context
def weights_recommend(ctx: Context, preset_name: str):
    """Get recommended weights for a preset."""
    
    try:
        verbose_print(f"Fetching recommended weights for '{preset_name}'", ctx.verbose)
        weights = ctx.client.get_recommended_weights(preset_name)
        
        if ctx.json_output:
            click.echo(format_json(weights))
        else:
            click.echo(f"Recommended weights for '{preset_name}':\n")
            for key, value in weights.items():
                click.echo(f"  {key}: {value}")
                
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


@weights.command('learned')
@click.argument('namespace_id')
@pass_context
def weights_learned(ctx: Context, namespace_id: str):
    """Get learned weights for a namespace."""
    
    try:
        verbose_print(f"Fetching learned weights for namespace {namespace_id}", ctx.verbose)
        weights = ctx.client.get_learned_weights(namespace_id)
        
        if ctx.json_output:
            click.echo(format_json(weights))
        else:
            if weights:
                click.echo(f"Learned weights for namespace {namespace_id}:\n")
                for key, value in weights.items():
                    click.echo(f"  {key}: {value}")
            else:
                click.echo(format_warning(f"No learned weights for namespace {namespace_id}", ctx.use_color))
                
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# OPTIMIZE COMMAND
# ============================================================================

@cli.command()
@click.option('--namespace', '-n', help='Namespace to optimize')
@pass_context
def optimize(ctx: Context, namespace: Optional[str]):
    """Trigger weight optimization.
    
    Examples:
    
        vex-memory optimize
        
        vex-memory optimize --namespace work
    """
    
    # Use default namespace from config if not provided
    if not namespace:
        namespace = ctx.config.get('default_namespace')
    
    try:
        verbose_print(f"Triggering optimization for namespace {namespace or 'default'}", ctx.verbose)
        result = ctx.client.optimize_weights(namespace_id=namespace)
        
        if ctx.json_output:
            click.echo(format_json(result))
        else:
            click.echo(format_success("✓ Optimization triggered", ctx.use_color))
            if 'status' in result:
                click.echo(f"  Status: {result['status']}")
            if 'message' in result:
                click.echo(f"  {result['message']}")
                
    except VexMemoryError as e:
        click.echo(format_error(str(e), ctx.use_color), err=True)
        sys.exit(1)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for CLI."""
    try:
        cli(obj=Context())
    except KeyboardInterrupt:
        click.echo("\n\nInterrupted.", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()