#!/bin/bash

set -euo pipefail

mkdir -p dist
cp firmware/boot_out.txt dist/
cp -a src/solar_simulator/. dist/

# cross-compile all .py files in lib/ via `mpy-cross`
find dist/lib -type f -name "*.py" ! -name "__init__.py" | while read -r pyfile; do
    echo "Compiling $pyfile -> ${pyfile%.py}.mpy"
    ./bin/mpy-cross "$pyfile"
    rm "$pyfile"
done

# cross-compile external dependencies via `circup` (listed under dependencies in pyproject.toml)
mkdir -p tmp
sed -n '/^dependencies *= *\[/,/\]/p' pyproject.toml | \
grep -o '"[^"]*"' | \
tr -d '"' | \
sed 's/[ \t]*[><=~].*//' > tmp/circup_reqs.txt

echo "Parse dependencies:"
cat tmp/circup_reqs.txt

if [ -s tmp/circup_reqs.txt ]; then
    echo "Installing depenencies via circup ..."
    circup --path dist install -r tmp/circup_reqs.txt
    rm -r tmp
else
    echo "No external production dependencies to install."
fi
