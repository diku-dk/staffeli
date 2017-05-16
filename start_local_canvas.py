#!/usr/bin/env python3

import subprocess
import sys
from typing import List

subprocess.check_call([
    "docker", "run",
    "--publish=3000:3000",
    "--interactive", "--tty", "--rm",
    "lbjay/canvas-docker"])
