#!/bin/bash

##
# This script downloads the CircuitPython-compatible mpy-cross binary from
# Adafruit's official bucket on AWS S3.
#
# The purpose of this script is two-fold:
#
#     1) to enable cross-compiling binaries locally instead of relying on
#        pre-compiled .mpy binaries
#
#     2) The `pip` installable version(s) of mpy-cross are explicitly not
#        recommended by the maintainers of circuitpython because it is built for
#        MicroPython.
#
# Requires: curl
#
# Further Reading:
# https://learn.adafruit.com/welcome-to-circuitpython/library-file-types-and-frozen-libraries#what-is-an-mpy-file-3117820)
#

set -euo pipefail

cp_version="$1"
os_arch="linux-amd64"
url="https://adafruit-circuit-python.s3.amazonaws.com/bin/mpy-cross/$os_arch/mpy-cross-$os_arch-$cp_version.static"
target_dir="bin"
target="$target_dir/mpy-cross"

mkdir -p "$target_dir"

if [ -f "${target}" ];
then
    echo "Binary already exists at '${target}'. Skipping."
    exit 0
fi

if ! curl -fsSL -o "$target" "$url";
then
    echo "Error: Failed to download binary." >&2
    echo "Verify that version '$cp_version' exists at the url '$url'." >&2
    rm -f "${target}"
    exit 1
fi

chmod +x "${target}"
echo "Successfully downloaded and configured: ${target}"
