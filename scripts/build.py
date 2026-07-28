#!/usr/bin/env python3

"""Build the project.

Locally cross-compiles dependencies and project sources to MicroPython bytecode.
"""

import importlib.resources
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

from circuitpython_build_tools.build import mpy_cross

PROJECT_DIR = Path("src/solar_simulator")
OUT_DIR = Path("build")

DEPENDENCIES = ["adafruit_ads1x15", "adafruit_mcp4728"]
LEAVE_UNCOMPILED = ["__init__.py", "boot.py", "code.py"]


def module_sources(name: str) -> tuple[bool, list[Path]]:
    """Resolve the source .py file(s) for an installed package/module."""
    spec = importlib.util.find_spec(name)

    if spec is None:
        raise FileNotFoundError(
            f"Couldn't find '{name}'. Is it pip-installed in this venv?"
        )

    # It's a multi-file package.
    if spec.submodule_search_locations:
        package_dir = importlib.resources.files(name)

        sources = sorted(
            Path(str(module))
            for module in package_dir.iterdir()
            if module.name.endswith(".py")
        )

        return True, sources

    # It's a single-file module.
    return False, [Path(spec.origin)]


def compile_module(name: str, mpy_cross_bin: str) -> None:
    """Cross-compile dependency modules."""
    is_package, sources = module_sources(name)

    for src in sources:
        dst_dir = OUT_DIR / "lib" / name if is_package else OUT_DIR / "lib"
        compile_or_copy(src, dst_dir, mpy_cross_bin)


def compile_project(project_dir: Path, mpy_cross_bin: str) -> None:
    """Cross-compile the Solar Simulator project's own lib/ sources."""
    for name in ("code.py", "boot.py"):
        src = project_dir / name
        if src.exists():
            compile_or_copy(src, OUT_DIR, mpy_cross_bin)

    lib_dir = project_dir / "lib"
    if lib_dir.is_dir():
        for src in sorted(lib_dir.rglob("*.py")):
            rel_dir = src.parent.relative_to(lib_dir)
            compile_or_copy(src, OUT_DIR / "lib" / rel_dir, mpy_cross_bin)


def compile_or_copy(src: Path, dst_dir: Path, mpy_cross_bin: str) -> None:
    """Copy or compile the contents of a package/module into .mpy byte-code.

    If the source is a file that shouldn't be compiled, just pass through.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)

    if src.name in LEAVE_UNCOMPILED:
        dst = dst_dir / src.name
        print(f"copy {src} -> {dst}")
        shutil.copyfile(src, dst)
        return

    # cross-compile using mpy-cross.
    dst = dst_dir / f"{src.stem}.mpy"
    print(f"mpy-cross {src} -> {dst}")
    subprocess.run([mpy_cross_bin, "-o", str(dst), str(src)], check=True) #  noqa: S603


def main(cp_version: str) -> None:
    """Entrypoint for script."""
    mpy_cross_bin = mpy_cross({"tag": cp_version, "name": cp_version})

    for module in DEPENDENCIES:
        compile_module(module, mpy_cross_bin)

    compile_project(PROJECT_DIR, mpy_cross_bin)


if __name__ == "__main__":
    main(sys.argv[1])
