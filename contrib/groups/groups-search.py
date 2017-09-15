#!/usr/bin/env python3
#
# Find which group a KU id is a member of.

import sys
import re
import os
import glob

import staffeli.canvas as canvas


course = canvas.Course()
can = canvas.Canvas()

def search(groups_file, ku_id):
    with open(groups_file) as f:
        contents = f.read().strip()
    groups = [line.split(' ') for line in contents.split('\n')]

    for users, i in zip(groups, range(len(groups))):
        if ku_id in users:
            print('{:03d}'.format(i))

    return 0

sys.exit(search(*sys.argv[1:]))
