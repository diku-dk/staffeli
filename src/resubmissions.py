#!/usr/bin/env python3

import os, os.path, re, shutil, sys, yaml

from assignment import get_cwd_assignment
from submission import find_student_id

import datetime

def _iso8601(datestr):
    return datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")

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

def download_last_graded(canvas, user_id, history, last_graded_path):
    sub_history = history['submission_history']
    last_graded = None
    for sub in sub_history:
        if sub['workflow_state'] == "graded":
            if last_graded == None or \
                    _iso8601(last_graded['graded_at']) < _iso8601(sub['graded_at']):
                last_graded = sub

    if last_graded == None:
        if len(sub_history) > 1 or not 'attachments' in sub_history[0]:
            print("Can't deduce last graded submission for {}.".format(user_id))
            return
        else:
            last_graded = sub_history[0]

    for attachment in last_graded['attachments']:
        path = os.path.join(last_graded_path, attachment['filename'])
        canvas.get_verified_file(path, attachment['url'])

def download_last_comment(canvas, user_id, history, last_graded_path):
    sub_comments = history['submission_comments']
    last_comment = None
    for comment in sub_comments:
        if not 'attachments' in comment or len(comment['attachments']) == 0:
            continue
        if last_comment == None or \
                _iso8601(last_comment['created_at']) < _iso8601(comment['created_at']):
            last_comment = comment

    if last_comment == None:
        if len(sub_comments) > 1 or not 'attachments' in sub_comments[0]:
            print("Can't deduce last comment for {}.".format(user_id))
            return
        else:
            last_comment = sub_comments[0]

    for attachment in last_comment['attachments']:
        path = os.path.join(last_graded_path, attachment['filename'])
        canvas.get_verified_file(path, attachment['url'])

def download_resub(assignment, resubsbase, graders, resub):
    canvas = assignment.canvas
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

    history = canvas.submission_history(assignment.course.id, assignment.id, user_id)
    history_path = os.path.join(dirpath, "history.yaml")
    with open(history_path, 'w') as outfile:
        yaml.dump(history, outfile)

    last_graded_path = os.path.join(dirpath, "last_graded")
    mkdirp(last_graded_path)

    download_last_graded(canvas, user_id, history, last_graded_path)
    download_last_comment(canvas, user_id, history, last_graded_path)

def download_all(assignment, resubs, subdirs):
    basename = os.path.basename(os.getcwd())

    resubsdir = os.path.join("..", "..", "resubs")
    mkdirp(resubsdir)

    resubsbase = os.path.join(resubsdir, basename)
    mkdirp(resubsbase)

    graders = grader_names(assignment.canvas, grader_ids(resubs))
    for grader in graders.values():
        graderbase = os.path.join(resubsbase, grader)
        mkdirp(graderbase)

    for resub in resubs:
        download_resub(assignment, resubsbase, graders, resub)

def main():
    assignment = get_cwd_assignment()
    course = assignment.course
    resubs = get_resubs(assignment)
    subdirs = get_subdirs()
    download_all(assignment, resubs, subdirs)

if __name__ == "__main__":
    main()
