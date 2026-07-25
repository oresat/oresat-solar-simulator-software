# Edit to match how your OS mounts the Pico.
BOARD_DIR := /media/$(USER)/CIRCUITPY
CP_VERSION = $(shell head -1 "$(BOARD_DIR)/boot_out.txt" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')

PHONY: build deploy clean test test-ci

build:
	python3 scripts/build.py $(CP_VERSION)

deploy: build
	cp -R build/* $(BOARD_DIR)/
	@echo "Deployment complete."

clean:
	@echo "Cleaning up cache, report, binaries, and distribution files ..."
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf bin/
	rm -rf build/
	rm -f *.coverage*
	rm -f *coverage*
	@echo "Clean up complete."

test:
	pytest tests/ -v --tb=short

test-ci:
	pytest tests/ -v --tb=long --cov=src/solar_simulator --cov-report=xml --cov-report=term
