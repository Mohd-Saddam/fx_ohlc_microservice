#!/bin/bash

# FX OHLC Microservice - Test Runner Script
# ==========================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     FX OHLC Microservice - Comprehensive Test Suite       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print section headers
print_section() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
}

# Function to check if Docker is running
check_docker() {
    print_section "Checking Docker Status"
    
    if ! docker ps > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running!${NC}"
        echo "Please start Docker and try again."
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Function to check if containers are up
check_containers() {
    print_section "Checking Service Containers"
    
    if ! docker-compose ps | grep -q "Up"; then
        echo -e "${YELLOW}⚠️  Containers not running. Starting services...${NC}"
        docker-compose up -d
        echo "Waiting 10 seconds for services to initialize..."
        sleep 10
    fi
    
    echo -e "${GREEN}✅ Containers are running${NC}"
    docker-compose ps
}

# Function to check health endpoint
check_health() {
    print_section "Checking Application Health"
    
    max_retries=5
    retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Application is healthy${NC}"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        echo "Waiting for application... (attempt $retry_count/$max_retries)"
        sleep 2
    done
    
    echo -e "${RED}❌ Application health check failed${NC}"
    echo "Please check the logs: docker-compose logs app"
    exit 1
}

# Function to run all tests
run_all_tests() {
    print_section "Running All Tests"
    pytest tests/ -v --tb=short
    return $?
}

# Function to run tests with coverage
run_with_coverage() {
    print_section "Running Tests with Coverage"
    pytest tests/ -v --cov=app --cov-report=html --cov-report=term
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
    fi
    
    return $?
}

# Function to run specific test file
run_test_file() {
    print_section "Running Test File: $1"
    pytest "tests/$1" -v
    return $?
}

# Function to run tests in parallel
run_parallel() {
    print_section "Running Tests in Parallel"
    
    if ! pip show pytest-xdist > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  pytest-xdist not installed. Installing...${NC}"
        pip install pytest-xdist
    fi
    
    pytest tests/ -n auto -v
    return $?
}

# Function to show test summary
show_summary() {
    print_section "Test Summary"
    
    echo "Test Files:"
    echo "  - test_tick_api.py:      Tick CRUD operations (27 tests)"
    echo "  - test_ohlc_api.py:      OHLC aggregation queries (31 tests)"
    echo "  - test_websocket_api.py: WebSocket functionality (25 tests)"
    echo "  - test_integration.py:   End-to-end workflows (25 tests)"
    echo ""
    echo "Total: 108+ tests"
}

# Parse command line arguments
case "${1:-all}" in
    all)
        check_docker
        check_containers
        check_health
        run_all_tests
        TEST_RESULT=$?
        ;;
    
    coverage)
        check_docker
        check_containers
        check_health
        run_with_coverage
        TEST_RESULT=$?
        ;;
    
    parallel)
        check_docker
        check_containers
        check_health
        run_parallel
        TEST_RESULT=$?
        ;;
    
    tick)
        check_docker
        check_containers
        check_health
        run_test_file "test_tick_api.py"
        TEST_RESULT=$?
        ;;
    
    ohlc)
        check_docker
        check_containers
        check_health
        run_test_file "test_ohlc_api.py"
        TEST_RESULT=$?
        ;;
    
    websocket)
        check_docker
        check_containers
        check_health
        run_test_file "test_websocket_api.py"
        TEST_RESULT=$?
        ;;
    
    integration)
        check_docker
        check_containers
        check_health
        run_test_file "test_integration.py"
        TEST_RESULT=$?
        ;;
    
    summary)
        show_summary
        TEST_RESULT=0
        ;;
    
    help|--help|-h)
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  all          Run all tests (default)"
        echo "  coverage     Run tests with coverage report"
        echo "  parallel     Run tests in parallel (faster)"
        echo "  tick         Run only Tick API tests"
        echo "  ohlc         Run only OHLC API tests"
        echo "  websocket    Run only WebSocket tests"
        echo "  integration  Run only integration tests"
        echo "  summary      Show test summary"
        echo "  help         Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 all        # Run all tests"
        echo "  $0 coverage   # Run with coverage"
        echo "  $0 tick       # Run only tick tests"
        echo ""
        TEST_RESULT=0
        ;;
    
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        echo "Use '$0 help' for usage information"
        TEST_RESULT=1
        ;;
esac

# Print final result
echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅  All Tests Passed Successfully!        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌  Some Tests Failed                     ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════╝${NC}"
fi

exit $TEST_RESULT
