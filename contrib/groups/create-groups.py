#!/usr/bin/env python3
#
# Create groups both on Canvas and locally.

import sys
import re
import os
import glob

import staffeli.canvas as canvas


course = canvas.Course()
can = canvas.Canvas()

# Mapping from abc123 (or whatever is before @ in the KU email address) to
# user id.
user_ids = {}
for s in can.all_students(course.id):
    m = re.match('^(.+?)@', s['login_id'])
    user_ids[m.group(1)] = s['id']

def create(subs_path, category_name, groups_file):
    # Extract groups.
    with open(groups_file) as f:
        contents = f.read().strip()
    groups = [line.split(' ') for line in contents.split('\n')]

    # Update Canvas.
    group_cats = can.group_categories(course.id)
    group_cat = next(filter(lambda cat: cat['name'] == category_name,
                            group_cats))
    group_cat_id = group_cat['id']

    for users, i in zip(groups, range(len(groups))):
        group_name = '{} {:03d}'.format(category_name, i)
        users = list(map(lambda abc123: user_ids[abc123], users))
        group = can.create_group(group_cat_id, group_name)
        group_id = group[0]['id']
        can.add_group_members(group_id, users)

    # Update locally.
    groupsubs_path = subs_path.replace('subs/', 'groupsubs/')
    os.makedirs(groupsubs_path, exist_ok=True)
    for users, i in zip(groups, range(len(groups))):
        groupsub_path = os.path.join(groupsubs_path, '{:03d}'.format(i))
        users_submitted = []
        for abc123 in users:
            pattern = os.path.join(subs_path, abc123) + '_*'
            subpaths = glob.glob(pattern)
            assert len(subpaths) == 1
            subpath = subpaths[0]
            if len(os.listdir(subpath)) > 1:
                # Ignore .staffeli.yml.
                users_submitted.append(subpath)
        assert len(users_submitted) == 1
        submitting_user_path = users_submitted[0]
        os.symlink(os.path.join('..', '..', submitting_user_path), groupsub_path)

    return 0

sys.exit(create(*sys.argv[1:]))
