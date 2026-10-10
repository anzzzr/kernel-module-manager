#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Standalone Live Demo Script for kernel-module-manager
# Runs the full Go daemon + Python AI service pipeline in DEMO_MODE=true.
# Can be executed on macOS, Linux, or Windows (WSL/Git Bash).
# ==============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}====================================================================${NC}"
echo -e "${CYAN}    Linux Kernel Module Diagnostic Manager — Live Pipeline Demo     ${NC}"
echo -e "${CYAN}====================================================================${NC}"

# 1. Environment Configuration
export DEMO_MODE=true
export PORT=8080
export MODULE_API_TOKEN="admin-secret-token"
export AI_SERVICE_PORT=8001
export AI_SERVICE_TOKEN="test-token"

export AI_SERVICE_URL="http://127.0.0.1:8001"
export RAG_ENABLED=true
export LLM_API_KEY="mock-key"

echo -e "\n${YELLOW}[1/4] Starting Python AI Microservice (port 8001)...${NC}"
PYTHONPATH=ai_service python3 -m uvicorn kernel_diagnostic_ai.main:app --port 8001 --host 127.0.0.1 > /tmp/kmm_ai_service.log 2>&1 &
AI_PID=$!

echo -e "${YELLOW}[2/4] Starting Go Diagnostic Host Daemon (port 8080)...${NC}"
go run main.go > /tmp/kmm_go_daemon.log 2>&1 &
GO_PID=$!

cleanup() {
    echo -e "\n${BLUE}==> Cleaning up background demo processes...${NC}"
    kill $AI_PID 2>/dev/null || true
    kill $GO_PID 2>/dev/null || true
}
trap cleanup EXIT

# Wait for services to become healthy
echo -e "${BLUE}Waiting for services to initialize...${NC}"
for i in {1..15}; do
    if curl -s http://127.0.0.1:8001/health >/dev/null && curl -s http://127.0.0.1:8080/health >/dev/null; then
        echo -e "${GREEN}✓ Both services healthy!${NC}"
        break
    fi
    sleep 0.5
done

echo -e "\n${YELLOW}[3/4] Sending Diagnostic Request for 'nvidia' (Canned Vermagic Mismatch)...${NC}"
echo -e "${CYAN}$ curl -s -X POST http://127.0.0.1:8080/module/nvidia/diagnose -H 'Authorization: Bearer admin-secret-token'${NC}\n"

RESP=$(curl -s -X POST http://127.0.0.1:8080/module/nvidia/diagnose \
    -H "Authorization: Bearer admin-secret-token")

echo "$RESP" | python3 -m json.tool

echo -e "\n${YELLOW}[4/4] Querying Live Observability Metrics (/stats)...${NC}"
echo -e "${CYAN}$ curl -s http://127.0.0.1:8080/stats${NC}"
curl -s http://127.0.0.1:8080/stats | python3 -m json.tool

echo -e "\n${CYAN}$ curl -s http://127.0.0.1:8001/stats${NC}"
curl -s http://127.0.0.1:8001/stats | python3 -m json.tool

echo -e "\n${GREEN}====================================================================${NC}"
echo -e "${GREEN}✓ End-to-End Demo Complete! Full pipeline verified in DEMO_MODE.${NC}"
echo -e "${GREEN}====================================================================${NC}"
