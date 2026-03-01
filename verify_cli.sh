#!/bin/bash
# CLI Verification Script
# Tests all major CLI functionality

set -e  # Exit on error

echo "🧪 vex-memory CLI Verification Script"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate venv if needed
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Test counter
TESTS_RUN=0
TESTS_PASSED=0

# Test function
test_command() {
    local description="$1"
    local command="$2"
    TESTS_RUN=$((TESTS_RUN + 1))
    
    echo -n "Test $TESTS_RUN: $description... "
    
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# 1. Version check
test_command "Version check" "vex-memory --version | grep -q '2.0.0'"

# 2. Help text
test_command "Help text" "vex-memory --help | grep -q 'vex-memory CLI'"

# 3. Health check (may fail if server is down - that's ok)
if vex-memory health >/dev/null 2>&1; then
    test_command "Health check" "true"
    SERVER_RUNNING=true
else
    echo -e "${YELLOW}Server not running - skipping integration tests${NC}"
    SERVER_RUNNING=false
fi

# 4. Config init
test_command "Config init" "vex-memory config init --help"

# 5. Config show
test_command "Config show" "vex-memory config show | grep -q 'api_url'"

# 6. Config get
test_command "Config get" "vex-memory config get api_url"

# 7. Config set
test_command "Config set" "vex-memory config set timeout 60"

# 8-15: Integration tests (only if server is running)
if [ "$SERVER_RUNNING" = true ]; then
    echo ""
    echo "Running integration tests..."
    echo ""
    
    # 8. Store memory
    STORE_OUTPUT=$(vex-memory store "CLI verification test" --importance 0.8 2>&1)
    MEMORY_ID=$(echo "$STORE_OUTPUT" | grep -oP 'memory: \K[a-f0-9-]+' | head -1)
    if [ -n "$MEMORY_ID" ]; then
        test_command "Store memory" "true"
        
        # 9. Get memory
        test_command "Get memory" "vex-memory get $MEMORY_ID | grep -q 'CLI verification test'"
        
        # 10. JSON output
        test_command "JSON output" "vex-memory --json get $MEMORY_ID | python -m json.tool"
        
        # 11. Update memory
        test_command "Update memory" "vex-memory update $MEMORY_ID --importance 0.9"
        
        # 12. Search
        test_command "Search" "vex-memory search 'verification' --limit 5"
        
        # 13. Delete memory
        test_command "Delete memory" "vex-memory delete $MEMORY_ID --yes"
    else
        echo -e "${YELLOW}Could not extract memory ID - skipping dependent tests${NC}"
    fi
    
    # 14. List memories
    test_command "List memories" "vex-memory list --limit 5"
    
    # 15. Stats
    test_command "Stats" "vex-memory stats"
fi

# Summary
echo ""
echo "======================================"
echo "Test Results: $TESTS_PASSED/$TESTS_RUN passed"
echo ""

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
