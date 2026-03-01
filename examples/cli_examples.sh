#!/bin/bash
# vex-memory CLI Examples

# ============================================================================
# Basic Operations
# ============================================================================

# Store a memory
vex-memory store "The project deadline is March 15th"

# Store with options
vex-memory store "Important meeting notes" \
  --importance 0.9 \
  --type episodic \
  --namespace "work" \
  --metadata '{"project":"vex","category":"meeting"}'

# Store from file
echo "Long content from file" > notes.txt
vex-memory store --file notes.txt --importance 0.7

# ============================================================================
# Searching
# ============================================================================

# Basic search
vex-memory search "project deadline"

# Search with filters
vex-memory search "meeting notes" \
  --limit 20 \
  --min-similarity 0.7 \
  --type episodic \
  --namespace "work"

# Search with JSON output
vex-memory --json search "deadline" --limit 5

# ============================================================================
# Listing Memories
# ============================================================================

# List recent memories
vex-memory list

# List with filters
vex-memory list --limit 50 --type episodic --namespace "work"

# List with pagination
vex-memory list --limit 20 --offset 40

# ============================================================================
# Getting a Memory
# ============================================================================

# Get memory by ID
vex-memory get abc123-def456-789...

# Get as JSON
vex-memory --json get abc123-def456-789...

# ============================================================================
# Updating Memories
# ============================================================================

# Update importance
vex-memory update abc123... --importance 0.9

# Update content
vex-memory update abc123... --content "Updated content"

# Update metadata
vex-memory update abc123... --metadata '{"reviewed":true}'

# ============================================================================
# Deleting Memories
# ============================================================================

# Delete with confirmation
vex-memory delete abc123...

# Delete without confirmation
vex-memory delete abc123... --yes

# ============================================================================
# Context Building
# ============================================================================

# Build context
vex-memory context "What is the project deadline?"

# Build context with options
vex-memory context "meeting notes" \
  --token-budget 4000 \
  --model "gpt-4" \
  --use-mmr \
  --diversity 0.6 \
  --namespace "work"

# Get context as JSON for LLM integration
vex-memory --json context "deadline" | jq -r '.formatted'

# ============================================================================
# Health & Stats
# ============================================================================

# Check server health
vex-memory health

# Get statistics
vex-memory stats

# Get stats for namespace
vex-memory stats --namespace "work"

# ============================================================================
# Configuration
# ============================================================================

# Initialize config file
vex-memory config init

# Show current config
vex-memory config show

# Get single value
vex-memory config get api_url

# Set values
vex-memory config set api_url "http://prod-server:8000"
vex-memory config set default_namespace "personal"
vex-memory config set timeout 60

# ============================================================================
# Namespaces
# ============================================================================

# Create namespace
vex-memory namespace create "work" --owner "my-agent"

# List namespaces
vex-memory namespace list

# Delete namespace
vex-memory namespace delete abc123... --yes

# ============================================================================
# Weights
# ============================================================================

# List available presets
vex-memory weights presets

# Get recommended weights
vex-memory weights recommend balanced

# Get learned weights for namespace
vex-memory weights learned abc123...

# ============================================================================
# Optimization
# ============================================================================

# Trigger optimization
vex-memory optimize

# Trigger optimization for namespace
vex-memory optimize --namespace "work"

# ============================================================================
# Global Options
# ============================================================================

# Use different server
vex-memory --base-url http://localhost:9000 health

# Verbose output
vex-memory --verbose store "Test memory"

# JSON output (works with most commands)
vex-memory --json search "test" --limit 5

# Disable colors
vex-memory --no-color list

# Custom timeout
vex-memory --timeout 60 search "slow query"

# ============================================================================
# Scripting Examples
# ============================================================================

# Store memories in bulk
for i in {1..10}; do
  vex-memory store "Bulk memory $i" --importance 0.5
done

# Export all memories as JSON
vex-memory --json list --limit 1000 > memories_backup.json

# Search and process results
vex-memory --json search "important" --limit 20 | \
  jq -r '.[] | select(.importance_score > 0.8) | .content'

# Get memory count
vex-memory --json stats | jq '.total_memories'

# Check if server is healthy
if vex-memory health >/dev/null 2>&1; then
  echo "Server is healthy"
else
  echo "Server is down"
fi
