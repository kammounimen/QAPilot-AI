ifeq ($(OS),Windows_NT)
  SHELL := cmd.exe
endif

BACKEND ?= file

.PHONY: up down lint cases sync gen-tests run defects push report repro all

up:
	docker compose up -d --build
	uv run python scripts/wait_for_app.py

down:
	docker compose down -v

lint:
	uv run ruff check .

cases:
	uv run python -m pipeline.gen_cases
	uv run python -m pipeline.check_cases

sync:
	uv run python -m pipeline.export --backend $(BACKEND)

gen-tests:
	uv run python -m pipeline.gen_tests
	uv run python -m pipeline.check_tests

# Suite bloquante : tout sauf les tests de défauts connus
run:
	uv run pytest tests/api tests/gold --ignore-glob="tests/gold/test_def_*" -q -rs --junitxml=reports/junit.xml

# Défauts connus : rouges volontairement, non bloquants
defects:
	-uv run pytest tests/gold/test_def_001.py tests/gold/test_def_002.py -q --junitxml=reports/junit_defects.xml

push:
	uv run python -m pipeline.push_results --backend $(BACKEND)

report:
	uv run python -m pipeline.report

# Preuve de reproductibilité : deux exécutions, puis comparaison des empreintes
repro:
	$(MAKE) sync
	$(MAKE) run
	$(MAKE) defects
	$(MAKE) push
	$(MAKE) report
	uv run python -m pipeline.repro snapshot run1
	$(MAKE) sync
	$(MAKE) run
	$(MAKE) defects
	$(MAKE) push
	$(MAKE) report
	uv run python -m pipeline.repro snapshot run2
	uv run python -m pipeline.repro compare run1 run2

all: lint up cases sync gen-tests run defects push report
