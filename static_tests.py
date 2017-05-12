#!/usr/bin/env python3

import subprocess
import sys
from typing import List

exitcode = 0


def run(command: List[str]) -> None:
    global exitcode
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        exitcode = 1

mypy_files = [
        "staffeli/names.py",
        "staffeli/cachable.py",
        "staffeli/upload.py",
        "tests/test_sections.py"
    ]

flake8_files = mypy_files + [
        "staffeli/files.py",
        "staffeli/assignment.py",
        "staffeli/listed.py"
    ]

run(["flake8"] + flake8_files)
run([
        "mypy",
        "--disallow-untyped-calls",
        "--disallow-untyped-defs",
        "--strict-optional",
        "--ignore-missing-imports"
    ] + mypy_files)

sys.exit(exitcode)