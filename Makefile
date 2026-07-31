CP_VERSION := 10.2.1
SRC_ROOT   := src/solar_simulator
LIB_ROOT   := $(SRC_ROOT)/lib
BUILD_ROOT := build
LIB_SRCS   := app.py solar_simulator.py utils.py
MODE_SRCS  := auto_mode.py basilisk_mode.py manual_mode.py
COPY_SRCS  := $(SRC_ROOT)/boot.py $(SRC_ROOT)/code.py $(wildcard $(LIB_ROOT)/__init__.py $(LIB_ROOT)/modes/__init__.py)

MPYFILES   := $(addprefix $(BUILD_ROOT)/lib/, $(LIB_SRCS:.py=.mpy)) $(addprefix $(BUILD_ROOT)/lib/modes/, $(MODE_SRCS:.py=.mpy))
PYFILES    := $(patsubst $(SRC_ROOT)/%, build/%, $(COPY_SRCS))

vpath %.py $(SRC_ROOT):$(SRC_ROOT)/lib

.PHONY: build deploy clean test test-ci

build: $(PYFILES) $(MPYFILES)

$(BUILD_ROOT)/%.mpy: %.py
	@mkdir -p $(dir $@)
	circuitpython-mpy-cross --circuitpython-version 10.x -o $@ $^

$(BUILD_ROOT)/modes/%.mpy: %.py
	@mkdir -p $(dir $@)
	circuitpython-mpy-cross --circuitpython-version 10.x -o $@ $^

build/%.py: $(SRC_ROOT)/%.py
	@mkdir -p $(dir $@)
	cp $< $@

deploy: build
	@BOARD_DIR=$$(findmnt -lo TARGET | grep CIRCUITPY); \
	if [ -z "$$BOARD_DIR" ]; then \
		echo "ERROR: Device path not found — is it mounted?"; \
		exit 1; \
	fi; \
	ACTUAL_VERSION=$$(head -1 "$$BOARD_DIR/boot_out.txt" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+'); \
	if [ "$$ACTUAL_VERSION" != "$(CP_VERSION)" ]; then \
		echo "ERROR: Device is running CircuitPython $$ACTUAL_VERSION, expected $(CP_VERSION)."; \
		exit 1; \
	fi; \
	cp -R build/* "$$BOARD_DIR/" && sync
	@echo "Deployment complete."

clean:
	@echo "Cleaning up build/ files ..."
	rm -rf build/

distclean:
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
