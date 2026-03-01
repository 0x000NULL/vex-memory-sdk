# vex-memory CLI Documentation

The vex-memory CLI provides a command-line interface for interacting with the vex-memory API.

## Installation

The CLI is installed automatically when you install the SDK:

```bash
pip install vex-memory-sdk
```

Verify installation:
```bash
vex-memory --version
```

## Quick Start

```bash
# Check server health
vex-memory health

# Store a memory
vex-memory store "The project deadline is March 15th"

# Search for memories
vex-memory search "project deadline"

# List recent memories
vex-memory list --limit 10

# Get a specific memory
vex-memory get <memory-id>
```

## Global Options

These options can be used with any command:

```bash
--base-url URL, -u URL      # Server URL (default: http://localhost:8000)
--timeout SECONDS, -T       # Request timeout (default: 30)
--verbose, -v               # Enable verbose output
--json                      # Output as JSON
--no-color                  # Disable colored output
--version                   # Show version
--help                      # Show help
```

Example:
```bash
vex-memory --base-url http://prod:8000 --json search "important"
```

## Configuration

The CLI can be configured using a config file at `~/.vex-memory/config.json`.

### Initialize Config

```bash
vex-memory config init
```

Creates default config file:
```json
{
  "api_url": "http://localhost:8000",
  "default_namespace": null,
  "default_importance": 0.5,
  "timeout": 30,
  "output_format": "table",
  "color": true
}
```

### View Config

```bash
# Show all configuration
vex-memory config show

# Get single value
vex-memory config get api_url
```

### Update Config

```bash
# Set configuration values
vex-memory config set api_url "http://localhost:9000"
vex-memory config set default_namespace "work"
vex-memory config set timeout 60
```

## Core Commands

### store - Store a New Memory

Store a memory with optional metadata and settings.

```bash
# Basic usage
vex-memory store "The project deadline is March 15th"

# With options
vex-memory store "Important meeting notes" \
  --importance 0.9 \
  --type episodic \
  --namespace "work" \
  --metadata '{"project":"vex","category":"meeting"}'

# From file
vex-memory store --file notes.txt --importance 0.7
```

**Options:**
- `--importance`, `-i`: Importance score (0.0-1.0, default: 0.5)
- `--type`, `-t`: Memory type (semantic/episodic/procedural/emotional)
- `--namespace`, `-n`: Namespace ID
- `--metadata`, `-m`: JSON metadata string
- `--file`, `-f`: Read content from file

### search - Search for Memories

Semantic search for relevant memories.

```bash
# Basic search
vex-memory search "project deadline"

# With filters
vex-memory search "meeting notes" \
  --limit 20 \
  --min-similarity 0.7 \
  --type episodic \
  --namespace "work" \
  --min-importance 0.5
```

**Options:**
- `--limit`, `-l`: Maximum results (default: 10)
- `--min-similarity`: Minimum similarity score (0.0-1.0, default: 0.5)
- `--type`, `-t`: Filter by memory type
- `--namespace`, `-n`: Filter by namespace
- `--min-importance`: Filter by minimum importance

**Output:**
```
Found 3 result(s):

[1] (importance: 0.90)
    The project deadline is March 15th
    Created: 2026-03-01

[2] (importance: 0.75)
    Meeting scheduled to discuss project timeline
    Created: 2026-02-28

[3] (importance: 0.60)
    Project kickoff notes
    Created: 2026-02-25
```

### get - Get Memory by ID

Retrieve a specific memory by its ID.

```bash
vex-memory get abc123-def456-789...
```

**Output:**
```
Memory ID: abc123-def456-789...
Type: episodic
Importance: 0.80
Created: 2026-03-01 12:00:00
Content:
  The project deadline is March 15th

Metadata:
  project: vex
  category: deadline
```

### list - List Recent Memories

List memories sorted by creation date (most recent first).

```bash
# List 10 most recent
vex-memory list

# With filters
vex-memory list --limit 50 --type episodic --namespace "work"

# With pagination
vex-memory list --limit 20 --offset 40
```

**Options:**
- `--limit`, `-l`: Maximum memories (default: 10)
- `--offset`: Skip first N memories (pagination)
- `--type`, `-t`: Filter by memory type
- `--namespace`, `-n`: Filter by namespace
- `--min-importance`: Filter by minimum importance

### update - Update a Memory

Update memory content, importance, or metadata.

```bash
# Update importance
vex-memory update abc123... --importance 0.9

# Update content
vex-memory update abc123... --content "Updated content"

# Update metadata
vex-memory update abc123... --metadata '{"reviewed":true}'

# Update multiple fields
vex-memory update abc123... \
  --content "New content" \
  --importance 0.95 \
  --metadata '{"status":"reviewed"}'
```

**Options:**
- `--content`, `-c`: New content
- `--importance`, `-i`: New importance score
- `--metadata`, `-m`: New metadata (JSON)

### delete - Delete a Memory

Delete a memory with optional confirmation.

```bash
# Delete with confirmation
vex-memory delete abc123...

# Skip confirmation
vex-memory delete abc123... --yes
```

**Options:**
- `--yes`, `-y`: Skip confirmation prompt

### context - Build Intelligent Context

Build optimized context for LLM queries.

```bash
# Basic usage
vex-memory context "What is the project deadline?"

# With options
vex-memory context "recent work" \
  --token-budget 4000 \
  --model "gpt-4" \
  --use-mmr \
  --mmr-lambda 0.7 \
  --diversity 0.6 \
  --namespace "work"

# Get formatted output for LLM
vex-memory --json context "deadline" | jq -r '.formatted'
```

**Options:**
- `--token-budget`, `-b`: Token budget (default: 4000)
- `--model`, `-m`: LLM model for token counting (default: gpt-4)
- `--use-mmr`: Use Maximal Marginal Relevance
- `--mmr-lambda`: MMR balance between relevance (1.0) and diversity (0.0)
- `--diversity`, `-d`: Diversity threshold (0.0-1.0, default: 0.7)
- `--min-score`: Minimum composite score
- `--namespace`, `-n`: Filter by namespace

**Output:**
```
Context (3 memories, 1,247 tokens, 31.2% utilization):

[2026-03-01] (score: 0.92)
  The project deadline is March 15th

[2026-02-28] (score: 0.85)
  Meeting to discuss timeline postponed

[2026-02-25] (score: 0.78)
  Project kickoff scheduled for March 1st
```

### health - Check Server Health

Check if the vex-memory server is running and healthy.

```bash
vex-memory health
```

**Output:**
```
Server: http://localhost:8000
Status: OK ✓
Database: Connected ✓
Memories: 1,247
Uptime: 5h 23m
```

### stats - Show Statistics

Display memory statistics and distribution.

```bash
# Overall stats
vex-memory stats

# Stats for specific namespace
vex-memory stats --namespace "work"
```

**Output:**
```
Memory Statistics:
  Total memories: 1,247
  
  By type:
    semantic: 842 (67.5%)
    episodic: 305 (24.5%)
    procedural: 78 (6.3%)
    emotional: 22 (1.8%)
  
  By importance:
    High (>0.8): 123 (9.9%)
    Medium (0.5-0.8): 654 (52.4%)
    Low (<0.5): 470 (37.7%)
  
  Namespaces: 12
  Average importance: 0.62
```

## Namespace Commands

Manage namespaces for organizing memories.

### Create Namespace

```bash
vex-memory namespace create "work" --owner "my-agent"
```

### List Namespaces

```bash
vex-memory namespace list
```

### Delete Namespace

```bash
vex-memory namespace delete abc123... --yes
```

## Weight Management

Manage context building weights and presets.

### List Weight Presets

```bash
vex-memory weights presets
```

Shows available presets:
- `balanced`: Balanced across all factors
- `relevance_focused`: Prioritizes similarity and importance
- `recency_focused`: Prioritizes recent memories
- `diversity_focused`: Maximizes variety

### Get Recommended Weights

```bash
vex-memory weights recommend balanced
```

### Get Learned Weights

Get auto-tuned weights for a namespace:

```bash
vex-memory weights learned abc123...
```

### Trigger Optimization

Trigger weight optimization for better results:

```bash
# Optimize default namespace
vex-memory optimize

# Optimize specific namespace
vex-memory optimize --namespace "work"
```

## JSON Output Mode

Most commands support `--json` for machine-readable output:

```bash
# Get JSON output
vex-memory --json search "test" --limit 5

# Process with jq
vex-memory --json list --limit 100 | \
  jq -r '.[] | select(.importance_score > 0.8) | .content'

# Export all memories
vex-memory --json list --limit 10000 > memories_backup.json

# Get memory count
vex-memory --json stats | jq '.total_memories'
```

## Scripting Examples

### Bulk Store Memories

```bash
#!/bin/bash
for i in {1..100}; do
  vex-memory store "Bulk memory $i" --importance 0.5
done
```

### Health Check Script

```bash
#!/bin/bash
if vex-memory health >/dev/null 2>&1; then
  echo "Server is healthy"
  exit 0
else
  echo "Server is down"
  exit 1
fi
```

### Export High-Importance Memories

```bash
#!/bin/bash
vex-memory --json list --limit 10000 | \
  jq -r '.[] | select(.importance_score > 0.8) | .content' > important_memories.txt
```

### Search and Format

```bash
#!/bin/bash
query="$1"
vex-memory --json search "$query" --limit 20 | \
  jq -r '.[] | "[\(.importance_score | tostring)] \(.content)"'
```

### Backup Script

```bash
#!/bin/bash
date=$(date +%Y%m%d)
vex-memory --json list --limit 100000 > "backup_${date}.json"
echo "Backed up $(jq '. | length' "backup_${date}.json") memories"
```

## Environment Variables

The CLI respects these environment variables:

- `VEX_MEMORY_URL`: Default API URL (overrides config)
- `VEX_MEMORY_TIMEOUT`: Default timeout in seconds

Example:
```bash
export VEX_MEMORY_URL="http://prod-server:8000"
export VEX_MEMORY_TIMEOUT=60

vex-memory health
```

## Troubleshooting

### Connection Errors

```bash
Error: Request failed: Connection refused
```

**Solution:** Check that the vex-memory server is running:
```bash
# Check server status
curl http://localhost:8000/health

# Or use health command with verbose
vex-memory --verbose health
```

### Invalid JSON Metadata

```bash
Error: Invalid JSON: ...
```

**Solution:** Ensure metadata is valid JSON:
```bash
# Good
vex-memory store "test" --metadata '{"key":"value"}'

# Bad (missing quotes)
vex-memory store "test" --metadata '{key:value}'
```

### Permission Denied (Config File)

**Solution:** Ensure config directory is writable:
```bash
mkdir -p ~/.vex-memory
chmod 755 ~/.vex-memory
```

## Advanced Usage

### Using Custom Server

```bash
# Connect to production server
vex-memory --base-url https://vex-memory.prod.example.com \
  search "important queries"

# Or set in config
vex-memory config set api_url "https://vex-memory.prod.example.com"
```

### Pipeline Integration

```bash
# Store from stdin
echo "New memory content" | vex-memory store -

# Search and pipe to LLM
vex-memory --json context "summarize recent work" | \
  jq -r '.formatted' | \
  curl -X POST https://api.openai.com/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d @-
```

### Monitoring Script

```bash
#!/bin/bash
# Monitor memory growth
while true; do
  count=$(vex-memory --json stats | jq '.total_memories')
  echo "$(date): $count memories"
  sleep 3600  # Check hourly
done
```

## See Also

- [Python SDK Documentation](README.md)
- [API Documentation](https://vexmemory.dev/docs)
- [Examples Directory](examples/)
