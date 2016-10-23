#!/usr/bin/env python3

import os, os.path, sys, yaml

def find_student_ids(subdir):
    jsonpath = os.path.join(subdir, "canvas_group.json")
    if os.path.isfile(jsonpath):
        with open(jsonpath, "r") as f:
            return json.load(f)
    else:
        return [find_student_id(subdir)]

def find_student_id(subdir):
    yamlpath = os.path.join(subdir, "canvas.yaml")
    if os.path.isfile(yamlpath):
        with open(yamlpath, "r") as f:
            return yaml.load(f)["user_id"]

    for filename in os.listdir(subdir):
        if filename.count("_") >= 3:
            filename = filename.replace("_late_", "_")
            parts = filename.split("_")
            return int(parts[1])
    raise LookupError("Can't find student id in \"{}\".".format(subdir))

def main():
    print(find_student_ids("."))

if __name__ == "__main__":
    main()
