# Edit this path to match how your OS mounts the Pico.
TARGET_DIR := "/media/$(USER)/CIRCUITPY"

upload: pico/code.py pico/boot.py pico/lib
	echo "$(TARGET_DIR)"
	cp -r pico/code.py -t $(TARGET_DIR)	
	cp -r pico/boot.py -t $(TARGET_DIR)	
	cp -r pico/lib -t $(TARGET_DIR)
	git log -1 | grep commit > "$(TARGET_DIR)/commit"

test:
	pytest tests/ -v --tb=short

test-ci:
	pytest tests/ -v --tb=long --cov=src/solar_simulator --cov-report=xml --cov-report=term
