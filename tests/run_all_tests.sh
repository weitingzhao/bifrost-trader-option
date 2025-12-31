#!/bin/bash
# Comprehensive test runner for all phases

set -e

echo "=========================================="
echo "Bifrost Implementation Verification Tests"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0
SKIPPED=0

# Function to run tests
run_test_suite() {
    local suite_name=$1
    local test_file=$2
    
    echo "----------------------------------------"
    echo "Running: $suite_name"
    echo "----------------------------------------"
    
    if [ -f "$test_file" ]; then
        if python3 -m pytest "$test_file" -v --tb=short; then
            echo -e "${GREEN}✓ $suite_name: PASSED${NC}"
            ((PASSED++))
        else
            echo -e "${RED}✗ $suite_name: FAILED${NC}"
            ((FAILED++))
        fi
    else
        echo -e "${YELLOW}⚠ $suite_name: Test file not found${NC}"
        ((SKIPPED++))
    fi
    echo ""
}

# Check if pytest is installed
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: pytest not installed. Installing...${NC}"
    pip install pytest > /dev/null 2>&1 || {
        echo -e "${RED}Error: Could not install pytest${NC}"
        exit 1
    }
fi

# Run Phase 1 tests
echo "=========================================="
echo "PHASE 1: Foundation Tests"
echo "=========================================="
run_test_suite "Phase 1: Foundation" "tests/test_phase1_foundation.py"

# Run Phase 2 tests
echo "=========================================="
echo "PHASE 2: Data Infrastructure Tests"
echo "=========================================="
run_test_suite "Phase 2: Data Infrastructure" "tests/test_phase2_data_infrastructure.py"

# Run Phase 3 tests
echo "=========================================="
echo "PHASE 3: Enhanced Features Tests"
echo "=========================================="
run_test_suite "Phase 3: Enhanced Features" "tests/test_phase3_enhanced_features.py"

# Summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi

