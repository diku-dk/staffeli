#!/usr/bin/env python3
#
# Create groups both on Canvas and locally.

import sys
import re
import os
import glob

import staffeli.canvas as canvaslib


debug = print

# Maps abc123 (or whatever before @ in KU email address) to Canvas User ID
def get_user_id_mapping(canvas, course):
    user_ids = {}
    for s in canvas.all_students(course.id):
        m = re.match('^(.+?)@', s['login_id'])
        user_ids[m.group(1)] = s['id']
    return user_ids

def create_groups_on_canvas(canvas, course, category_name, user_ids, groups):
    group_cats = canvas.group_categories(course.id)
    group_cat = next(filter(lambda cat: cat['name'] == category_name, group_cats))
    group_cat_id = group_cat['id']

    canvas_groups = canvas.groups(group_cat_id)
    debug("There are {} groups for category {} ({}) already: {}".format(
        len(canvas_groups),
        category_name,
        group_cat_id,
        ", ".join(map(lambda group: group['name'], canvas_groups))))

    for group_users, i in zip(groups, range(len(groups))):
        group_name = '{} {:03d}'.format(category_name, i)
        group_user_ids = list(map(lambda abc123: user_ids[abc123], group_users))

        try:
            debug("Creating group '{}'. ".format(group_name), end='')
            group = canvas.create_group(group_cat_id, group_name)
            group_id = group[0]['id']

            debug("Adding group members {} to group: {}".format(
                ", ".join(group_users), str(group)))
            canvas.add_group_members(group_id, group_user_ids)
        except Exception as wat:
            print("Failed.")
            print(wat)


# create('subs/N/', 'Assignment N Groups', 'subs/N/groups.txt')
def create(subs_path, category_name, groups_file):
    canvas = canvaslib.Canvas()
    course = canvaslib.Course()

    # Get mapping from abc123 to Canvas User ID.
    user_ids = get_user_id_mapping(canvas, course)

    # Extract groups.
    with open(groups_file) as f:
        contents = f.read().strip()
    groups = [line.split(' ') for line in contents.split('\n')]

    # Update Canvas.
    create_groups_on_canvas(canvas, course, category_name, user_ids, groups)

    # Update locally.
    groupsubs_path = subs_path.replace('subs/', 'groupsubs/')
    os.makedirs(groupsubs_path, exist_ok=True)
    for group_members, group_number in zip(groups, range(len(groups))):
        groupsub_path = os.path.join(groupsubs_path, '{:03d}'.format(group_number))
        group_members_submitted = []
        total_count = 0
        for abc123 in group_members:
            pattern = os.path.join(subs_path, abc123) + '_*'
            subpaths = glob.glob(pattern)

            # There should be 0 or 1 directories that match.
            # 0 if, for some reason, a KU ID specified in a group.txt doesn't
            #   have a submission. (This can be for other reasons than that it
            #   is an invalid KU ID, or that that KU ID isn't subscribed to the
            #   course. Example: cbh239 is on Advanced Programming 2017 and was
            #   mentioned in a group.txt, they didn't submit anything
            #   themselves for assignment 1, but they don't have an empty
            #   directory like other students.
            if len(subpaths) > 1:
                raise Exception('Wait! Two submissions match {}: {}'.format(
                    abc123, ", ".join(subpaths)))

            elif len(subpaths) == 1:
                subpath = subpaths[0]
                ignore_files = [".staffeli.yml", "group.txt"]
                files = [ f for f in os.listdir(subpath) if f not in ignore_files ]
                if len(files) > 0:
                    group_members_submitted.append(subpath)

        if len(group_members_submitted) != 1:
            raise Exception('Wait! Multiple submissions from {}: {}'.format(
                ", ".join(group_members),
                ", ".join(group_members_submitted)))

        submitter_path = group_members_submitted[0]
        os.symlink(os.path.join('..', '..', submitter_path), groupsub_path)

    return 0

if __name__ == "__main__":
    sys.exit(create(*sys.argv[1:]))
