#!/usr/bin/env python3

import os.path, yaml, sys, re

from canvas import Canvas

def config_dir(parent, filename):
    for i in range(5):
        if os.path.isfile(os.path.join(parent, filename)):
            return parent
        parent = os.path.join("..", parent)
    raise LookupError("Couldn't locate a {} file.".format(filename))

def dir_name(name):
    name = re.sub("[^a-zA-Z0-9-]", '_', name)
    if os.path.exists(name):
        raise Exception(
            "You already got a directory or file named '{}'.\n \
            Please rename or remove this in order to set up TA environment.".format(name))
    return name

def get_set_id(name, sets):
    for s in sets:
        if name == 'Dybber/Athas gruppe-test':
            name = 'ass1'
        if not ('name' in s and 'id' in s):
            raise LookupError("Set is missing the fields: 'name' or 'id'.")
        if s['name'] == name:
            return s['id']

    raise LookupError("No Group Set named '{}'.".format(name))

def get_members(name, ass, course_id, api_token):
    # we should probably store the group categorie id in assignment's canvas.yaml
    group_sets  = ass.canvas.group_categories(course_id)
    group_set_id = get_set_id(ass.json['name'], group_sets)

    # get ids of all groups in a group set 
    groups = ass.canvas.groups(group_set_id)
    group_id = get_set_id(name, groups)

    return Canvas(api_token).group_members(group_id)

def make_sub_dirs(name, subs):
    for i in range(len(subs)):
        sub_dir = os.path.join(name , str(i))
        os.makedirs(sub_dir)

        with open(os.path.join(sub_dir, "canvas.yaml"), "w") as f:
            yaml.dump(subs[i], f, default_flow_style=False)

def init_assignment(ass, name):

    assignment_dir = dir_name(ass)
    os.mkdir(assignment_dir)

    course_dir = config_dir(".", "canvas.yaml")    
    with open(os.path.join(course_dir, "canvas.yaml"), "r") as f:
        conf = yaml.load(f)
    course_id = conf['id']

#    with open(os.path.join(course_dir, "token"), "r") as f:
#        api_token = f.read().strip()

    assignment = Canvas().course(
        id = course_id).assignment(
            name = ass)

    subs = assignment.submissions()

    # get the ids of the students in
    # group set <assignment name>, group <instructor name>
    #members = get_members(name, assignment, course_id, api_token)
    #student_ids  = [m['id'] for m in members]

    #subs = [sub for sub in subs if sub['user_id'] in student_ids]
    make_sub_dirs(assignment_dir, subs)

    return subs


def main():
    try:
        ass = sys.argv[1]
        name = "" #sys.argv[2]
    except IndexError:
        print('error: wrong arguments', file=sys.stderr)
        print('usage: canvasTA-subs.py ASSIGNMENT_NAME',
              file=sys.stderr)
        return 1

    init_assignment(ass, name)
    print("TA environment for assignment {} was succesfully set up.".format(ass))
    return 0

if __name__ == "__main__":
    sys.exit(main())
