#!/usr/bin/env python3

# Copyright 2016-2017 DIKU, DIKUNIX
# Licensed under the EUPL v.1.1 only (the "Licence");
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# http://ec.europa.eu/idabc/eupl.html
# or
# https://web.archive.org/web/20160822183947/http://ec.europa.eu/idabc/eupl.html
# or see it verbatim in LICENSE.md.

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


files = ["staffeli.py", ".static_tests.py"]

run(["flake8"] + files)
run([
        "mypy",
        "--disallow-untyped-calls",
        "--disallow-untyped-defs",
        "--strict-optional",
        "--ignore-missing-imports"
    ] + files)

sys.exit(exitcode)
