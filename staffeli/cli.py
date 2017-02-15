import argparse, os, os.path, shutil, yaml, sys, re

from staffeli import canvas

from urllib.request import urlretrieve

from slugify import slugify

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def mknewdir(path):
    if os.path.exists(path):
        raise Exception((
                "There already exists a file or directory \"{}\".\n" +
                "Please rename or remove this first."
            ).format(path))
    os.mkdir(path)

def cache(o, dirpath):
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
    o.cache(dirpath)

def clone(args):
    dirname = " ".join(args)

    course = canvas.Canvas().course(name = dirname)
    mknewdir(dirname)
    course.cache(dirname)

    os.chdir(dirname)
    fetch_students(course)
    fetch_groups(course)

def fetch_students(course):
    print("Fetching students..")
    cache(course.list_students(), "students")

def fetch_groups(course):
    print("Fetching group categories..")
    gcs = course.list_group_categories()
    cache(gcs, "groups")

    print("Fetching group lists for each category..")
    for gc in gcs.json:
        print("Fetching {}..".format(gc['name']))
        gs = canvas.GroupList(course, id = gc['id'])
        gs.cache(os.path.join("groups", gc['name'] + ".yml"))

def fetch_group(course, name):
    gs = canvas.GroupList(course, name = name)
    mkdir("groups")
    path = os.path.join("groups", gs.name + ".yml")
    gs.cache(path)
    print("Fetched {} as {}.".format(name, path))

def fetch_all_subs(course):
    print("Fetching all assignments..")
    assigns = course.list_assignments()
    mkdir("subs")
    for assign in assigns:
        if assign['grading_type'] == 'not_graded':
            continue
        print("Fetching {}..".format(assign['name']))
        assign = canvas.Assignment(course, id = assign['id'])
        dirname = slugify(assign.displayname.replace('/', '_'))
        path = os.path.join("subs", dirname)
        mkdir(path)
        assign.cache(path)

def fetch_attachments(path, attachments):
    for att in attachments:
        targetpath = os.path.join(path, att['filename'])
        print("Downloading {}..".format(targetpath))
        if os.path.isfile(targetpath):
            print("Skipped. Looks like it is already here.")
            # TODO: Do this smarter
            continue
        urlretrieve(att['url'], targetpath)

def fetch_sub(students, path, sub, metadata = False):
    json = sub.json
    sid = json['user_id']
    if (not sid in students) or \
            (not 'kuid' in students[sid]):
        print("There is something wrong with {}.. Skipping".format(sid))
        print("Looks like this is a Test Student..")
        print("Try and have a look in SpeedGrader(tm):\n{}".format(json['preview_url']))
        print(sub)
        return
    subpath = os.path.join(path, "{}_{}".format(students[sid]['kuid'], sid))
    mkdir(subpath)
    sub.cache(subpath)
    if not metadata:
        if not 'attachments' in json:
            print("There is something wrong with {}.. Skipping".format(sid))
            print("This might be a 'No submission' submission.")
            print("Try and have a look in SpeedGrader(tm):\n{}".format(json['preview_url']))
            print(sub)
            return
        fetch_attachments(subpath, json['attachments'])

def fetch_subs(course, name, deep = False, metadata = False):
    name = slugify(name)
    path = os.path.join("subs", name)
    if os.path.isdir(path):
      assign = canvas.Assignment(course, path = path)
    else:
      assign = canvas.Assignment(course, name = name)
    mkdir("subs")
    mkdir(path)
    assign.cache(path)
    print("Fetched {} as {}.".format(name, path))
    if not deep:
        return

    students = canvas.StudentList(searchdir = "students").mapping
    for sub in assign.subs:
        fetch_sub(students, path, sub, metadata)

def fetch(args, metadata):
    course = canvas.Course()
    what = args[0]
    args = args[1:]
    if '/' in what:
        partition = what.partition('/')
        what = partition[0]
        args.insert(0, partition[2])
    if what == "students":
        fetch_students(course)
    elif what == "groups":
        fetch_groups(course)
    elif what == "group":
        fetch_group(course, " ".join(args))
    elif what == "subs":
        if len(args) == 0:
            fetch_all_subs(course)
        else:
            fetch_subs(course, " ".join(args).strip('/'), deep = True,
                metadata = metadata == True)
    else:
        raise Exception("Don't yet know how to fetch {}.".format(str(args)))

def copySub(uid, dst):
  uid = str(uid)
  for root, _, files in os.walk(subsdir):
    for f in files:
      if uid in f:
        dst = os.path.join(dst, os.path.basename(root))
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(root, dst, symlinks=True)
        return

def student_dirname(student):
    return "{}_{}".format(student['kuid'], student['id'])

def normalize_pathname(pathname):
    return pathname.replace("/", "_")

def split_according_to_groups(course, subspath, path):
    if not os.path.isdir(subspath):
        subspath = os.path.join("subs", subspath)
        if not os.path.isdir(subspath):
            raise LookupError("Can't resolve subs directory.")

    subsid = os.path.split(subspath)[1]

    splitpath = os.path.join("splits", subsid)
    mkdir("splits")
    mkdir(splitpath)

    gl = canvas.GroupList(course, path = path)
    teams = gl.uidmap()
    students = canvas.StudentList(searchdir = "students").mapping

    for name, uids in teams.items():
        name = normalize_pathname(name)
        namepath = os.path.join(splitpath, name)
        mkdir(namepath)
        for uid in uids:
            dirname = student_dirname(students[uid])
            subpath = os.path.join(subspath, dirname)
            if os.path.isdir(subpath):
                src = os.path.relpath(subpath, namepath)
                tgt = os.path.join(namepath, dirname)
                os.symlink(src, tgt)

def main_args_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=
"""
git-style, git-compatible command-line interface for canvas.

start a working area
    clone   Create a local clone for a course

update a working area
    fetch   Fetch something that might have changed

Grade a submission:
    grade GRADE [-m COMMENT] [FILEPATH]...

    Where
        GRADE           pass, fail, or an int.
        [-m COMMENT]    An optional comment to write.
        [FILEPATH]...   Optional files to upload alongside.
""")
    parser.add_argument(
        "action", metavar="ACTION",
        help="the action to perform")
    parser.add_argument(
        "--metadata", action='store_true',
        help="fetch metadata only")
    return parser

def parse_action_arg(parser, args):
    args, remargs = parser.parse_known_args(args)
    if args.action == "help":
        parser.print_help()
        sys.exit(0)
    return args, remargs

def groupsplit(args):
    split_according_to_groups(canvas.Course(), args[0], args[1])

def _check_grade(grade):
    goodgrades = ["pass", "fail"]
    if not grade in goodgrades:
        try:
            x = int(grade)
        except ValueError:
            print((
                "\"{}\" is a bad grade. Acceptable grades are: \"{}\", or an int."
                ).format(grade, "\", \"".join(goodgrades)))
            sys.exit(1)
    return grade

def _check_filepaths(filepaths):
    for filepath in filepaths:
        if not os.path.isfile(filepath):
            print("\"{}\" is not a file. What is this?".format(filepath))
            sys.exit(1)
    return filepaths

def grade_args_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="")
    parser.add_argument(
        "-m", metavar="COMMENT", dest='message', default="See attached files.")
    parser.add_argument(
        "grade", metavar="GRADE")
    return parser

def grade(args):
    args, remargs = grade_args_parser().parse_known_args(args)
    grade = _check_grade(args.grade)
    filepaths = _check_filepaths(remargs)
    message = args.message

    course = canvas.Course()
    assignment = canvas.Assignment(course)
    submission = canvas.Submission()
    for student_id in submission.student_ids:
        assignment.give_feedback(student_id, grade,
            message, filepaths, use_post = True)

def main():
    parser = main_args_parser()
    args, remargs = parse_action_arg(parser, sys.argv[1:])
    action = args.action

    if action == "clone":
        clone(remargs)
    elif action == "fetch":
        fetch(remargs, args.metadata)
    elif action == "grade":
        grade(remargs)
    elif action == "groupsplit":
        groupsplit(remargs)
    else:
        print("Unknown action {}.".format(action))
        parser.print_usage()

if __name__ == "__main__":
    main()
