BOARD_DIR := $(shell findmnt -lo TARGET | grep CIRCUITPY)
CP_VERSION = 10.2.1

PHONY: build deploy clean test test-ci

build:
	python3 scripts/build.py $(CP_VERSION)

deploy: build
	@if [ -z "$(BOARD_DIR)" ]; then \
		echo "ERROR: Device path not found — is it mounted?"; \
		exit 1; \
	fi; \
	ACTUAL_VERSION=$$(head -1 "$(BOARD_DIR)/boot_out.txt" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+'); \
	if [ "$$ACTUAL_VERSION" != "$(CP_VERSION)" ]; then \
		echo "ERROR: Device is running CircuitPython $$ACTUAL_VERSION, expected $(CP_VERSION)."; \
		exit 1; \
	fi
	cp -R build/* $(BOARD_DIR)/ && sync
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

# test:
# 	pytest tests/ -v --tb=short

# test-ci:
# 	pytest tests/ -v --tb=long --cov=src/solar_simulator --cov-report=xml --cov-report=term
