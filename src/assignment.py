#!/usr/bin/env python3

import os.path, yaml

from canvas import Canvas

def canvas_yaml_dir(parent):
    for i in range(5):
        if os.path.isfile(os.path.join(parent, "canvas.yaml")):
            return parent
        parent = os.path.join("..", parent)
    raise LookupError("Couldn't locate a canvas.yaml.")

def get_cwd_assignment():
    assignment_dir = canvas_yaml_dir(".")

    with open(os.path.join(assignment_dir, "canvas.yaml"), "r") as f:
        conf = yaml.load(f)
    assignment_id = conf['assignment_id']

    course_dir = canvas_yaml_dir(os.path.join(assignment_dir, ".."))

    with open(os.path.join(course_dir, "canvas.yaml"), "r") as f:
        conf = yaml.load(f)
    course_id = conf['course_id']

    assignment = Canvas().course(
        id = course_id).assignment(
            id = assignment_id)
    return assignment

def main():
    print(get_cwd_assignment().json)

if __name__ == "__main__":
    main()
