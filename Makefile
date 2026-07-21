# Edit to match how your OS mounts the Pico.
BOARD_DIR := /media/$(USER)/CIRCUITPY
CP_VERSION = head -1 "$(BOARD_DIR)/boot_out.txt" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+'

fetch-boot-out:
	@cp $(BOARD_DIR)/boot_out.txt firmware/
	@echo "SUCCESS: boot_out.txt fetched from the pico device.\n"
	@cat firmware/boot_out.txt

fetch-mpy-cross:
	@bash ./scripts/fetch-mpy-cross.sh $$($(CP_VERSION))

clean:
	@echo "Cleaning up cache, report, binaries, and distribution files ..."
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf bin/
	rm -rf dist/
	rm -f *.coverage*
	rm -f *coverage*
	@echo "Clean up complete."

test:
	@pytest tests/ -v --tb=short

test-ci:
	@pytest tests/ -v --tb=long --cov=src/solar_simulator --cov-report=xml --cov-report=term

lint:
	@ruff check

build: fetch-boot-out fetch-mpy-cross
	@bash ./scripts/build.sh

deploy: build
	@cp -a dist/. $(BOARD_DIR)/

upload: pico/code.py pico/boot.py pico/lib
	echo "$(BOARD_DIR)"
	cp -r pico/code.py -t $(BOARD_DIR)	
	cp -r pico/boot.py -t $(BOARD_DIR)	
	cp -r pico/lib -t $(BOARD_DIR)
	git log -1 | grep commit > "$(BOARD_DIR)/commit"
