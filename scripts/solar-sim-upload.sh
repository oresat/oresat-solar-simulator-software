#!/bin/bash
#tell the system that this is a bash script

#ex. running from git root dir
#   bash scripts/solar-sim-upload.sh PATH/TO/REPO
#   cd /home/$USER/solar-simulator-software && bash scripts/solar-sim-upload.sh .
set -euo pipefail
#good practice, helps the script crash when there are bugs to prevent silently blowing things up
#set -x
#un comment if you want to echo each line to the terminal for debugging

TARGET_DIR="/run/media/$USER/CIRCUITPY"
#fully qualified path to the pico

if [ "$#" -lt 1 ]
then
  echo "No arguments supplied"
  exit 1
fi

#TODO: complain if no argument is passed
SOURCE_DIR="$1/pico"
#fully qualified path to the local repo

TO_UPLOAD=("code.py" "boot.py" "lib")
#both files and directories

echo "> over-write following files/dirs $TARGET_DIR/[${TO_UPLOAD[@]}]?"
#warn the user about what we're about to do
read -p "> y/n " answer
#ask for user input, store the response in 'answer'

if [ "$answer" = "y" ]; then
    echo "[*] writing to $TARGET_DIR"
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

#copy commit hash to make identifying code on the pico easier
git log -1 | grep commit > "$TARGET_DIR/commit"

sync
sync
