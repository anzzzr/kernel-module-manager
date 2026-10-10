.PHONY: test lint eval demo up down help

help:
	@echo "Kernel Module Manager - Developer Commands:"
	@echo "  make test   - Run Go and Python unit tests"
	@echo "  make lint   - Run Go vet and Ruff linter"
	@echo "  make eval   - Run RAG benchmark harness with mock LLM (no secrets needed)"
	@echo "  make demo   - Run standalone demo mode verification"
	@echo "  make up     - Build and run services in Docker Compose (DEMO_MODE=true)"
	@echo "  make down   - Stop Docker Compose services"

test:
	@echo "==> Running Go unit and security tests..."
	go test ./... -v
	@echo "==> Running Python AI microservice tests..."
	@bash -c "source ai_service/.venv/bin/activate && PYTHONPATH=. pytest eval/test_metrics.py eval/test_injection.py ai_service/tests/ -v"

lint:
	@echo "==> Linting Go codebase..."
	go vet ./...
	@echo "==> Linting Python codebase with Ruff..."
	@bash -c "source ai_service/.venv/bin/activate && ruff check --config ai_service/pyproject.toml ai_service/ eval/"

eval:
	@echo "==> Running offline evaluation smoke benchmark (mock LLM, no secrets)..."
	@bash -c "source ai_service/.venv/bin/activate && PYTHONPATH=. python3 eval/run_eval.py --mode all --mock-llm"


demo:
	@echo "==> Executing standalone DEMO_MODE verification..."
	@DEMO_MODE=true go test ./modules -run TestDemoModeEvidence -v
	@echo "==> Demo mode verified successfully."

up:
	docker compose up -d --build

down:
	docker compose down
