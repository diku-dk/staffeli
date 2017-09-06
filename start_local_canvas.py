#!/usr/bin/env python3

import subprocess

subprocess.check_call([
    "docker", "run",
    "--publish=3000:3000",
    "--interactive", "--tty", "--rm",
    "lbjay/canvas-docker"])
