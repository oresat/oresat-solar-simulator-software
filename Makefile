CIRCUITPYTHON_VERSION := 10
BUILD := build
SRC   := src/solar_simulator
PACKAGES = adafruit_ads1x15 adafruit_mcp4728 adafruit_ticks asyncio

# External package dependencies.
SITE_PACKAGES := $(shell python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
SEARCH := $(addprefix $(SITE_PACKAGES)/, $(addsuffix *.py, $(PACKAGES)) $(addsuffix /*.py, $(PACKAGES)))
PKG_SRC := $(wildcard $(SEARCH))
PKG_DST := $(PKG_SRC:$(SITE_PACKAGES)/%.py=$(BUILD)/%.mpy)

COPY_SRC := $(addprefix $(SRC)/, boot.py code.py)
COPY_DST := $(COPY_SRC:$(SRC)/%.py=$(BUILD)/%.py)

COMP_SRC := $(filter-out $(COPY_SRC), $(wildcard $(SRC)/*))
COMP_DST := $(COMP_SRC:$(SRC)/%.py=$(BUILD)/%.mpy)

.PHONY: write clean distclean

$(BUILD): $(PKG_DST) $(COPY_DST) $(COMP_DST)

$(BUILD)/%.mpy: $(SITE_PACKAGES)/%.py
	@mkdir -p ${dir $@}
	circuitpython-mpy-cross --circuitpython-version $(CIRCUITPYTHON_VERSION).x -o $@ $^

$(BUILD)/%.mpy: $(SRC)/%.py
	@mkdir -p ${dir $@}
	circuitpython-mpy-cross --circuitpython-version $(CIRCUITPYTHON_VERSION).x -o $@ $^

$(BUILD)/%.py: $(SRC)/%.py
	@mkdir -p ${dir $@}
	cp $^ $@

write: $(BUILD)
	@BOARD_DIR=$$(findmnt --noheadings --source LABEL=CIRCUITPY --output TARGET); \
	if [ -z "$$BOARD_DIR" ]; then \
		echo "ERROR: Device path with disk label 'CIRCUITPY' not found — is it mounted?"; \
		exit 19; \
	fi; \
	if [ ! -f "$$BOARD_DIR/boot_out.txt" ]; then \
		echo "ERROR: $$BOARD_DIR/boot_out.txt not found -- cannot determine CircuitPython version on device."; \
		exit 2; \
	fi; \
	ACTUAL_VERSION=$$(sed -n 's/^Adafruit CircuitPython \([0-9]\+\)\..*/\1/p' $$BOARD_DIR/boot_out.txt); \
	if [ "$$ACTUAL_VERSION" != "$(CIRCUITPYTHON_VERSION)" ]; then \
		echo "ERROR: Device is running CircuitPython version $$ACTUAL_VERSION.x.x, expected version $(CIRCUITPYTHON_VERSION).x.x."; \
		exit 1; \
	fi; \
	find $$BOARD_DIR/ -mindepth 1 -not -name boot_out.txt -delete; \
	git rev-parse HEAD > $$BOARD_DIR/commit; \
	cp -Rv build/* "$$BOARD_DIR/" && sync

clean:
	rm -rf build/

distclean: clean
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -f *.coverage*
	rm -f *coverage*
