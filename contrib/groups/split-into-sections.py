#!/usr/bin/env python3
#
# Split into sections.

import sys
import re
import os

import staffeli.canvas as canvas


course = canvas.Course()
can = canvas.Canvas()

def create(groupsubs_path, groups_file, *section_names):
    sections_path = groupsubs_path.replace('groupsubs/', 'sections/')

    with open(groups_file) as f:
        contents = f.read().strip()
    groups = [line.split(' ') for line in contents.split('\n')]

    groups_distributed = []

    all_sections = can.list_sections(course.id)
    for name in section_names:
        section = next(filter(lambda sec: sec['name'] == name,
                              all_sections))

        m = re.match(r'Class (.+)', name)
        if m is not None:
            name = m.group(1).lower()

        section_path = os.path.join(sections_path, name)
        os.makedirs(section_path, exist_ok=True)

        ku_ids = [u['login_id'].split('@')[0] for u in section['students']]
        for group_members, group_id in zip(groups, range(len(groups))):
            # Base the section on the first member of the group.  This is
            # probably also what Canvas does.
            main_member = group_members[0]

            groupsub_path = os.path.join(groupsubs_path, '{:03d}'.format(group_id))
            section_sub_path = os.path.join(section_path, '{:03d}'.format(group_id))
            if main_member in ku_ids:
                os.symlink(os.path.join('..', '..', '..', groupsub_path), section_sub_path)
                groups_distributed.append(group_id)

    for group_members, group_id in zip(groups, range(len(groups))):
        if not group_id in groups_distributed:
            print('Error: The group consisting of {} was not put into any section.'.format(group_members))

    return 0

sys.exit(create(*sys.argv[1:]))
