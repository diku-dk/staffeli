import argparse, os, os.path, shutil, yaml, sys, re, random

from staffeli import canvas

from urllib.request import urlretrieve

from slugify import slugify

import Levenshtein as levenshtein

from bs4 import BeautifulSoup

if os.name == "nt":
    import _winapi

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

def clone(remargs):
    if len(remargs) == 1:
        course_name = remargs[0]
        dirname = course_name
    elif len(remargs) == 2:
        course_name = remargs[0]
        dirname = remargs[1]
    else:
        print("Usage: staffeli clone 'COURSE NAME' [DIRECTORY], or see: staffeli help")
        sys.exit(1)

    course = canvas.Canvas().course(name = course_name)
    mknewdir(dirname)
    course.cache(dirname)

    print("Cloning '{}' into '{}'...".format(course.displayname, dirname))

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
        dirname = slugify(assign.displayname.replace(os.sep, '_'))
        path = os.path.join("subs", dirname)
        mkdir(path)
        assign.cache(path)

def fetch_attachments(path, attachments):
    for att in attachments:
        targetpath = os.path.join(path, att['filename'])
        print("Downloading {}..".format(targetpath))
        if os.path.isfile(targetpath):
            # TODO: Do this smarter.  Check if the file is the same, or if it is
            # a new file!
            new_dir = 'new-download'
            i = 1
            while True:
                targetdir = os.path.join(path, new_dir)
                targetpath = os.path.join(targetdir, att['filename'])
                if os.path.exists(targetpath):
                    new_dir = 'new-download-{}'.format(i)
                    i += 1
                else:
                    os.makedirs(targetdir, exist_ok=True)
                    break
            print("Looks like it is already here. Putting it in a new directory '{}'.".format(new_dir))

        urlretrieve(att['url'], targetpath)

def write_body(path: str, body: str) -> None:
    with open(os.path.join(path, 'body.txt'), 'w') as f:
        soup = BeautifulSoup(body, 'html.parser')
        f.write(soup.text.strip() + "\n")

def fetch_sub(students, path, sub, metadata = False):
    json = sub.json
    if json['workflow_state'] == 'unsubmitted' or json['submission_type'] is None:
        return
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
    if metadata:
        return
    sub_type = json['submission_type']
    if sub_type == 'online_text_entry':
        write_body(subpath, json['body'])
    elif sub_type == 'online_upload':
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
    what = args[0].rstrip(os.sep)
    args = args[1:]
    if os.sep in what:
        partition = os.path.split(what)
        what = partition[0]
        args.insert(0, partition[1])
    args = list(map(lambda s: s.rstrip(os.sep), args))
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
            fetch_subs(course, " ".join(args), deep = True,
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
    return pathname.replace(os.sep  , "_")

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
            if not uid in students:
                continue
            dirname = student_dirname(students[uid])
            subpath = os.path.join(subspath, dirname)
            if os.path.isdir(subpath):
                src = subpath
                tgt = os.path.join(namepath, dirname)
                shutil.copytree(src, tgt, symlinks=True)

def main_args_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=
"""
git-style, git-compatible command-line interface for canvas.

Create a local working area for a course:
    clone 'COURSE NAME' [DIRECTORY]

    Where
        'COURSE NAME'   (An unambiguous, case-insensitive substring of)
                        the course name as it appears on your dashboard.
        [DIRECTORY]     An optional destination directory that defaults
                        to the first argument.

    For example:

        $ staffeli clone 'Advanced programming' ap17

Update a working area:
    fetch   Fetch something that might have changed

Grade a submission:
    grade GRADE [-m COMMENT] [-1] [FILEPATH]...

    Where
        GRADE           pass, fail, incomplete, or an int.
        [-m COMMENT]    An optional comment to write.
        [-f FILEPATH]   Upload the contents of a file as a comment.
        [-1]            Only upload feedback for 1 student id (instead of all).
        [FILEPATH]...   Optional files to upload alongside.

Work with groups:
    group add group GROUP_CATEGORY GROUP_NAME
        Add a new group to an *existing* group category.

    group set members GROUP_NAME USER...
        Set the members of a group.  Ignores any current members.

    group delete all groups GROUP_CATEGORY

Work with sections:
    section add member SECTION_NAME USER
        Add a user to a section.

    section randomise SECTION_NAME...
        Put students in sections of approx. equal size at random.

Work with users:
    user find USER_NAME
        Check if the user exists.  If not, make a guess.
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

def group(args):
    if len(args) == 4 and args[0] == 'add' and args[1] == 'group':
        add_group(args[2], args[3])

    if len(args) >= 4 and args[0] == 'set' and args[1] == 'members':
        set_group_members(args[2], args[3:])

    if len(args) == 4 and args[0] == 'delete' and args[1] == 'all' and args[2] == 'groups':
        delete_all_groups(args[3])

def section(args):
    if len(args) == 4 and args[0] == 'add' and args[1] == 'member':
        add_member_to_section(args[2], args[3])

    if len(args) >= 3 and args[0] == 'randomise':
        add_students_to_sections_random(args[1:])

def add_group(group_category_name, group_name):
    course = canvas.Course()

    can = canvas.Canvas()
    categories_all = can.group_categories(course.id)
    categories = list(filter(lambda x: x['name'] == group_category_name,
                             categories_all))
    if len(categories) < 1:
        raise Exception('no category of that name')
    else:
        group_category_id = categories[0]['id']

    can.create_group(group_category_id, group_name)

    fetch_groups(course) # a bit silly, and very slow

def set_group_members(group_name, user_names):
    course = canvas.Course()

    can = canvas.Canvas()
    groups_all = can.groups_in_course(course.id)
    groups = list(filter(lambda x: x['name'] == group_name,
                         groups_all))
    if len(groups) < 1:
        raise Exception('no group of that name')
    else:
        group_id = groups[0]['id']

    users_all = list(can.list_students(course.id))
    user_ids = []
    for user_name in user_names:
        users = list(filter(lambda x: x['name'] == user_name,
                            users_all))
        if len(users) < 1:
            raise Exception('no user of that name')
        else:
            user_id = users[0]['id']
        user_ids.append(user_id)
    can.add_group_members(group_id, user_ids)

    fetch_groups(course) # a bit silly, and very slow

def delete_all_groups(group_category_name):
    course = canvas.Course()
    can = canvas.Canvas()

    categories_all = can.group_categories(course.id)
    categories = list(filter(lambda x: x['name'] == group_category_name,
                             categories_all))
    if len(categories) < 1:
        raise Exception('no category of that name')
    else:
        group_category_id = categories[0]['id']

    can.delete_all_groups(group_category_id)

    fetch_groups(course) # a bit silly, and very slow

def find_section_id(section_name):
    course = canvas.Course()
    can = canvas.Canvas()

    sections_all = can.course_sections(course.id)
    sections = list(filter(lambda x: x['name'] == section_name,
                           sections_all))
    if len(sections) < 1:
        raise Exception('no section of that name')
    else:
        section_id = sections[0]['id']
    return section_id

def add_member_to_section(section_name, user_name):
    course = canvas.Course()
    can = canvas.Canvas()

    section_id = find_section_id(section_name)

    users_all = list(can.list_students(course.id))
    users = list(filter(lambda x: (x['name'] == user_name or
                                   x['login_id'][:6] == user_name),
                        users_all))
    if len(users) < 1:
        raise Exception('no user of that name')
    else:
        user_id = users[0]['id']
    can.add_section_member(section_id, user_id)

# This functionality should maybe not be part of the main staffeli code, as it
# can be composed just fine by the existing parts of staffeli.
def add_students_to_sections_random(section_names):
    course = canvas.Course()
    can = canvas.Canvas()

    section_ids = {section_name: find_section_id(section_name)
                   for section_name in section_names}

    users_all = list(can.list_students(course.id))

    random.shuffle(users_all)
    users_slice_start = 0
    for section_name, n_sections_remaining in zip(
            section_names, range(len(section_ids), 0, -1)):
        n_users_remaining = len(users_all) - users_slice_start
        section_size = n_users_remaining // n_sections_remaining
        section_id = section_ids[section_name]
        section_users = users_all[users_slice_start:users_slice_start + section_size]
        print('Section {} (id: {}) gets {} students: {}'.format(
            repr(section_name), section_id, section_size,
            ', '.join(u['name'] for u in section_users)))
        for user in section_users:
            can.add_section_member(section_id, user['id'])
        users_slice_start += section_size

def user(args):
    if len(args) == 2 and args[0] == 'find':
        find_user(args[1])

def find_user(user_name):
    course = canvas.Course()
    can = canvas.Canvas()
    users = list(can.list_students(course.id))

    # Hack to remove duplicates.
    users_found = list(filter(lambda user: user_name == user['name'] or user_name == user['login_id'][:6], users))
    users_found = list(set(tuple(x.items()) for x in users_found))
    users_found = [{k: v for k, v in x} for x in users_found]
    if len(users_found) == 1:
        print('Found; id: {}, sis_user_id: {}, sis_login_id: {}, name: {}'.format(
            users_found[0]['id'], users_found[0]['sis_user_id'],
            users_found[0]['sis_login_id'], users_found[0]['name']))
    elif len(users_found) > 1:
        print('{} users found:'.format(len(users_found)))
        for user in users_found:
            print(user)
        sys.exit(1)
    else:
        print('No users found.  Guesses:')
        users.sort(key=lambda user: levenshtein.ratio(user_name, user['name']),
                   reverse=True)
        for user in users[:10]:
            print('{:.2%} match; id: {}, sis_user_id: {}, sis_login_id: {}, name: {}'.format(
                levenshtein.ratio(user_name, user['name']),
                user['id'], user['sis_user_id'],
                user['sis_login_id'], user['name']))

        sys.exit(1)

def groupsplit(args):
    split_according_to_groups(canvas.Course(), args[0], args[1])

def _check_grade(grade):
    goodgrades = ["pass", "fail", "incomplete"]
    if not grade in goodgrades:
        try:
            x = int(grade)
        except ValueError:
            print((
                "\"{}\" is a bad grade. Acceptable grades are: \"{}\", or an int."
                ).format(grade, "\", \"".join(goodgrades)))
            sys.exit(1)

def _check_filepaths(filepaths):
    for filepath in filepaths:
        if not os.path.isfile(filepath):
            print("\"{}\" is not a file. What is this?".format(filepath))
            sys.exit(1)

def grade_args_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter, description='')

    parser.add_argument('grade', metavar='GRADE')
    parser.add_argument('attachments', nargs='*')
    parser.add_argument('-1', action='store_true', dest='one', default=False)

    comments = parser.add_mutually_exclusive_group(required=True)
    comments.add_argument('-m', metavar='COMMENT', dest='comment')
    comments.add_argument('-f', metavar='FILEPATH', dest='comment_file')
    comments.add_argument('--no-feedback', action='store_true')

    return parser

def grade(args):
    args, _ = grade_args_parser().parse_known_args(args)

    _check_grade(args.grade)
    _check_filepaths(args.attachments)

    if args.comment:
        comment = args.comment
    elif args.comment_file:
        _check_filepaths([args.comment_file])
        with open(args.comment_file) as f:
            comment = f.read()
    elif args.attachments:
        comment = "See attached file{}.".format(
            "" if len(args.attachments) == 1 else "s")
    else:
        comment = None

    course = canvas.Course()
    assignment = canvas.Assignment(course)
    submission = canvas.Submission()
    student_ids = submission.student_ids
    if args.one:
        student_ids = student_ids[:1]
    for sub in assignment.submissions():
        if sub['user_id'] in student_ids:
            current_grade = sub['grade']
            if current_grade == grade:
                print('Already graded.')
                course.canvas.show_verification_urls(
                    course.id, assignment.id, sub['user_id'])
                return
    for student_id in student_ids:
        assignment.give_feedback(student_id, args.grade, comment, args.attachments, use_post=True)

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
    elif action == "group":
        group(remargs)
    elif action == "section":
        section(remargs)
    elif action == "user":
        user(remargs)
    elif action == "groupsplit":
        groupsplit(remargs)
    else:
        print("Unknown action {}.".format(action))
        parser.print_usage()

if __name__ == "__main__":
    main()
