# Edit this path to match how your OS mounts the Pico.
TARGET_PATH ?= /media/$(USER)/CIRCUITPY
SOURCE_PATH := src
ENTRY_FILES := $(SOURCE_PATH)/main.py $(SOURCE_PATH)/boot.py

ALL_SOURCES := $(wildcard $(SOURCE_PATH)/*.py)
COMPILABLE_SOURCES := $(filter-out $(ENTRY_FILES), $(ALL_SOURCES))
OBJS := $(COMPILABLE_SOURCES:.py=.mpy)

.PHONY: all clean deploy

all: $(OBJS)
# Compile .mpy from .py
%.mpy: %.py
	@echo "Compiling $< -> $@"
	mpy-cross -o $@ $<

clean:
	rm -f $(OBJS)

deploy: all
	@echo "Deploying to $(TARGET_PATH) ..."

	@if [ ! -d "$(TARGET_PATH)" ]; then \
		echo "Error: $(TARGET_PATH) not found! Check your path and USB connection."; \
		exit 1; \
	fi

	@for file in $(OBJS) $(ENTRY_FILES); do \
		echo "Copying $$file ..."; \
		cp $$file $(TARGET_PATH)/; \
	done

	@echo "Deployment complete."
