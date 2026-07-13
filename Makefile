# Edit this path to match how your OS mounts the Pico.
TARGET_PATH ?= "/media/$(USER)/CIRCUITPY"

upload: src/code.py src/boot.py src/lib
	@echo "Deploying to $(TARGET_PATH) ..."

	@cp -r src/code.py -t $(TARGET_PATH)	
	@cp -r src/boot.py -t $(TARGET_PATH)	
	@cp -r src/lib -t $(TARGET_PATH)

	@echo "Deployment complete."
