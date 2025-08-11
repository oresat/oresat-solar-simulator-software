#!/bin/bash
#tell the system that this is a bash script

set -euo pipefail
#good practice, helps the script crash when there are bugs to prevent silently blowing things up
#set -x
#un comment if you want to echo each line to the terminal for debugging

TARGET_DIR="/run/media/monitor/CIRCUITPY"
#fully qualified path to the pico

SOURCE_DIR="/home/monitor/oresat-solar-simulator-software/pico"
#fully qualified path to the local repo

TO_UPLOAD=("code.py" "boot.py" "lib")
#both files and directories



#clear out what's in the pico
echo "> are you sure you want to clear this directory? ( rm -rf $TARGET_DIR/* )?"
#warn the user about what we're about to do
read -p "> y/n " answer
#ask for user input, store the response in 'answer'

if [ "$answer" = "y" ]; then
    echo "[*] emptying $TARGET_DIR"
    rm -rf $TARGET_DIR/*
else
    echo "[*] quitting..."
    exit
fi

#for every file and dir we want to move
for file in ${TO_UPLOAD[@]}; do
    echo "[*] copying $SOURCE_DIR/$file to $TARGET_DIR/$file"
    #-r to make copy recursive, so it works on directories
    cp -r $SOURCE_DIR/$file $TARGET_DIR/$file
done
