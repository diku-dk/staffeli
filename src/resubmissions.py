#!/usr/bin/env python3

import os, os.path, re, shutil, sys, yaml

from assignment import get_cwd_assignment
from submission import find_student_id

def get_subdirs():
    parent = "."
    subs = {}
    for name in os.listdir(parent):
        path = os.path.join(parent, name)

        if not os.path.isdir(path):
            continue

        try:
            subs[find_student_id(path)] = name
        except LookupError:

            # Hotfix for ill-formed AP subs
            for subdir in os.listdir(path):
                path = os.path.join(path, subdir)
                if os.path.isdir(path):
                    subs[find_student_id(path)] = name
    return subs

def get_resubs(assignment):
    resubs = []
    for sub in assignment.submissions():
        if sub["grade_matches_current_submission"] == False:
            resubs.append(sub)
    return resubs

def download_resub(resub, subdir):
    dst = os.path.join(subdir, "resub" + str(resub['attempt']))
    shutil.rmtree(dst, ignore_errors=True)
    os.mkdir(dst)

def mkdirp(path):
    if os.path.isdir(path):
        return
    if os.path.isfile(path):
        raise Exception("Can't create directory {}: path refers to a file.")
    os.mkdir(path)

def grader_ids(resubs):
    grader_ids = set()
    for resub in resubs:
        grader_ids.add(resub['grader_id'])
    return grader_ids

def grader_names(canvas, grader_ids):
    names = {}
    for grader_id in grader_ids:
        name = canvas.user(grader_id)['name']
        name = re.sub('[^a-z0-9]', '', name, flags=re.IGNORECASE).lower()
        name = "{}_{}".format(name, grader_id)
        names[grader_id] = name
    return names

def download_resub(canvas, resubsbase, graders, resub):
    user_id = resub['user_id']
    dirpath = os.path.join(resubsbase,
            graders[resub['grader_id']],
            str(user_id)   # TODO: Use a better name.
        )
    mkdirp(dirpath)
    print("Downloading {}".format(dirpath))

    for attachment in resub['attachments']:
        path = os.path.join(dirpath, attachment['filename'])
        canvas.get_verified_file(path, attachment['url'])

    canvas_path = os.path.join(dirpath, "canvas.yaml")
    with open(canvas_path, 'w') as outfile:
        yaml.dump(resub, outfile)

def download_all(canvas, resubs, subdirs):
    basename = os.path.basename(os.getcwd())

    resubsdir = os.path.join("..", "..", "resubs")
    mkdirp(resubsdir)

    resubsbase = os.path.join(resubsdir, basename)
    mkdirp(resubsbase)

    graders = grader_names(canvas, grader_ids(resubs))
    for grader in graders.values():
        graderbase = os.path.join(resubsbase, grader)
        mkdirp(graderbase)

    for resub in resubs:
        download_resub(canvas, resubsbase, graders, resub)

def main():
    assignment = get_cwd_assignment()
    course = assignment.course
    resubs = get_resubs(assignment)
    subdirs = get_subdirs()
    download_all(assignment.canvas, resubs, subdirs)

if __name__ == "__main__":
    main()
