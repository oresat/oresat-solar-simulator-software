CP_MAJOR_VERSION := 10
SRC_ROOT         := src/solar_simulator
LIB_ROOT         := $(SRC_ROOT)/lib
BUILD_ROOT       := build
LIB_SRCS         := app.py solar_simulator.py utils.py
MODE_SRCS        := auto_mode.py basilisk_mode.py manual_mode.py
COPY_SRCS        := $(SRC_ROOT)/boot.py $(SRC_ROOT)/code.py $(SRC_ROOT)/__init__.py $(wildcard $(LIB_ROOT)/__init__.py $(LIB_ROOT)/modes/__init__.py)

# External package dependencies.
SITE_PACKAGES    := $(shell python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
ADS1X15_PKG      := $(SITE_PACKAGES)/adafruit_ads1x15
ADS1X15_PY       := $(wildcard $(ADS1X15_PKG)/*.py)
ADS1X15_MPY      := $(patsubst $(ADS1X15_PKG)/%.py, $(BUILD_ROOT)/lib/adafruit_ads1x15/%.mpy, $(ADS1X15_PY))
MCP4728_PY       := $(SITE_PACKAGES)/adafruit_mcp4728.py
MCP4728_MPY      := $(BUILD_ROOT)/lib/adafruit_mcp4728.mpy

MPYFILES         := $(addprefix $(BUILD_ROOT)/lib/, $(LIB_SRCS:.py=.mpy)) $(addprefix $(BUILD_ROOT)/lib/modes/, $(MODE_SRCS:.py=.mpy)) $(ADS1X15_MPY) $(MCP4728_MPY)
PYFILES          := $(patsubst $(SRC_ROOT)/%, build/%, $(COPY_SRCS))

vpath %.py $(SRC_ROOT):$(SRC_ROOT)/lib

.PHONY: build deploy clean test test-ci

build: $(PYFILES) $(MPYFILES)

$(BUILD_ROOT)/%.mpy: %.py
	@mkdir -p $(dir $@)
	circuitpython-mpy-cross --circuitpython-version 10.x -o $@ $^

$(BUILD_ROOT)/modes/%.mpy: %.py
	@mkdir -p $(dir $@)
	circuitpython-mpy-cross --circuitpython-version 10.x -o $@ $^

$(BUILD_ROOT)/lib/adafruit_ads1x15/%.mpy: $(ADS1X15_PKG)/%.py
	@mkdir -p $(dir $@)
	circuitpython-mpy-cross --circuitpython-version 10.x -o $@ $<

$(BUILD_ROOT)/lib/adafruit_mcp4728.mpy: $(MCP4728_PY)
	@mkdir -p $(dir $@)
	circuitpython-mpy-cross --circuitpython-version 10.x -o $@ $<

build/%.py: $(SRC_ROOT)/%.py
	@mkdir -p $(dir $@)
	cp $< $@

write: build
	@BOARD_DIR=$$(findmnt --noheadings --source LABEL=CIRCUITPY --output TARGET); \
	if [ -z "$$BOARD_DIR" ]; then \
		echo "ERROR: Device path with disk label 'CIRCUITPY' not found — is it mounted?"; \
		exit 1; \
	fi; \
	if [ ! -f "$$BOARD_DIR/boot_out.txt" ]; then \
		echo "ERROR: $$BOARD_DIR/boot_out.txt not found -- cannot determine CircuitPython version on device."; \
		exit 1; \
	fi; \
	ACTUAL_MAJOR_VERSION=$$(head -1 "$$BOARD_DIR/boot_out.txt" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | cut -d. -f1); \
	if [ "$$ACTUAL_MAJOR_VERSION" != "$(CP_MAJOR_VERSION)" ]; then \
		echo "ERROR: Device is running CircuitPython version $$ACTUAL_MAJOR_VERSION.x.x, expected version $(CP_MAJOR_VERSION).x.x."; \
		exit 1; \
	fi; \
	git log -1 | grep commit > $$BOARD_DIR/commit && \
	cp -Rv build/* "$$BOARD_DIR/" && sync
	@echo "SUCCESS: Solar Simulator build written to device."

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
