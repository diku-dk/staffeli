#!/usr/bin/env python3

import copy
import json
import os
import requests
import sys
import time
import urllib.parse
import urllib.request
import yaml
import pdb

from os.path import basename

from staffeli import cachable, files, listed, names, upload

def format_json(d):
    return json.dumps(d, sort_keys=True, indent=2, ensure_ascii=False)

def _api_bool(value: bool) -> int:
    if value:
        return 1
    else:
        return 0

def _req(token, method, api_base, url_relative, url_absolute=None, **args):
    try:
        args = args['_arg_list']
    except KeyError:
        pass
    if type(args) == type({}):
        args = list(args.items())

    # In the case of list-returning API calls, maximize the number of entries
    # returned.  100 appears to be the max in at least one instance.  Combine
    # this with the 'all_pages=True' argument in calling '_call_api'.
    args.append(('per_page', 100))

    query_string = urllib.parse.urlencode(args, safe='[]@', doseq=True).encode('utf-8')

    if url_absolute is not None:
        url = url_absolute
    else:
        url = api_base + url_relative
    headers = {
        'Authorization': 'Bearer ' + token
    }
    return urllib.request.Request(url, data=query_string, method=method,
                                 headers=headers)

def _parse_pagination_link(s):
    link, rel = s.split('; rel="')
    link = link[1:-1]
    rel = rel[:-1]
    return (rel, link)

def _call_api(token, method, api_base, url_relative, all_pages=False, **args):
    req = _req(token, method, api_base, url_relative, None, **args)
    entries = []
    while True:
        with urllib.request.urlopen(req) as f:
            data = json.loads(f.read().decode('utf-8'))
            if type(data) is list:
                entries.extend(data)
            else:
                entries.append(data)

            # In some cases we want to extract many entries, e.g. the students
            # in a course.  However, some Absalon instances set a per_page limit
            # to 100, so we cannot just set per_page to 9000 and hope for the
            # best.  Instead we utilize the API's pagination facilities
            # documented at
            # <https://canvas.instructure.com/doc/api/file.pagination.html>.
            # This works, although it is not foolproof in the extreme case that
            # entries are added or removed from Absalon between our requests.
            # This is probably not something to worry about.
            if all_pages:
                pagination_links = {rel: link
                                    for rel, link in
                                    (_parse_pagination_link(s)
                                     for s in f.info()['Link'].split(','))}
                if pagination_links['current'] == pagination_links['last']:
                    break
                else:
                    url_absolute = pagination_links['next']
                    req = _req(token, method, api_base, None, url_absolute, **args)
            else:
                break
    if len(entries) == 1 and all_pages == False:
        return entries[0]
    else:
        return entries

def _upload_transit(course, filepath):
    form_url = "https://file-transit.appspot.com/upload"
    params = {
        'course': course
    }
    with open(filepath, "rb") as f:
        resp = requests.post(
            form_url, params=params, files=[('file', f)])
    if resp.status_code != 200:
        raise Exception(
            "Something is wrong with the file-transit service :-( " +
                resp.headers)

    print("Transitting {} to Canvas via {}".format(filepath, resp.url))

    return resp.url

def _upload_via_url(token, api_base, url_relative, filepath, viaurl):

    url = api_base + url_relative
    headers = {
        'Authorization': 'Bearer ' + token
    }

    name = basename(filepath)
    size = os.stat(filepath).st_size

    params = {
        'url'     : viaurl,
        'name'    : name,
        'size'    : size
    }

    resp = requests.post(url, headers=headers, params=params)

    json = resp.json()

    id = json['id']
    status_url = json['status_url']

    while json['upload_status'] == 'pending':
      print("Waiting for Canvas to download it..")
      time.sleep(3)
      json = requests.get(status_url, headers=headers).json()

    if json['upload_status'] != 'ready':
        raise Exception("Canvas refused to upload the file(s):\n{}". format(json))

    print("Canvas got it!")

    attachment = json['attachment']

    return attachment['id']

def _upload_submission_comment_file(
        token, api_base, url_relative, course, filepath, use_post = False):
    if use_post:
        return upload.via_post(
            api_base,
            url_relative + "/comments/files",
            token,
            filepath)
    else:
        viaurl = _upload_transit(course, filepath)
        return _upload_via_url(
            token, api_base,
            url_relative + "/comments/files",
            filepath, viaurl)

class GroupList(listed.ListedEntity, cachable.CachableEntity):
    def __init__(self, course, path = None, name = None, id = None):
        self.cachename = 'groups'
        self.canvas = course.canvas

        if path != None:
            cachable.CachableEntity.__init__(self, self.cachename, path, walk = False)
        else:
            if id != None:
                self.id = id
            else:
                entities = self.canvas.group_categories(course.id)
                listed.ListedEntity.__init__(self, entities, name)

            self.json = self.canvas.groups(self.id)

        for group in self.json:
            group['members'] = self.canvas.group_members(group['id'])

    def uidmap(self):
        mapping = {}
        for group in self.json:
            name = group['name']
            mapping[name] = map(lambda m: m['id'], group['members'])
        return mapping

    def publicjson(self):
        return { self.cachename : self.json }

class GroupCategoryList(cachable.CachableEntity):
    def __init__(self, canvas, course_id):
        self.json = canvas.group_categories(course_id)

    def publicjson(self):
        json = copy.deepcopy(self.json)
        for cat in json:
            del cat['is_member']
        return { 'group_categories': json }

class Course(listed.ListedEntity, cachable.CachableEntity):
    def __init__(self, canvas = None, name = None, id = None):

        if canvas == None:
            canvas = Canvas()

        self.canvas = canvas
        self.cachename = 'course'

        if name == None and id == None:
            cachable.CachableEntity.__init__(self, self.cachename)
            listed.ListedEntity.__init__(self)
        else:
            entities = self.canvas.courses()
            listed.ListedEntity.__init__(self, entities, name, id)

        self.id = self.json['id']
        self.displayname = self.json['name']

    def assignment(self, name = None, id = None):
        return Assignment(self, name, id)

    def list_assignments(self):
        return self.canvas.list_assignments(self.id)

    def list_students(self):
        return StudentList(self)

    def list_group_categories(self):
        return GroupCategoryList(self.canvas, self.id)

    def group(self, name = None, id = None):
        return Group(self.canvas, name, id)

    def publicjson(self):
        json = copy.deepcopy(self.json)
        del json['enrollments']
        return { self.cachename : json }

class StudentList(cachable.CachableEntity):
    def __init__(self, course = None, searchdir = "."):
        self.cachename = 'students'

        if course == None:
            cachable.CachableEntity.__init__(self, self.cachename, searchdir)
        else:
            self.json = course.canvas.all_students(course.id)

        self.mapping = {}
        for student in self.json:
            sid = student['id']
            self.mapping[sid] = student
            if 'login_id' in student:
                self.mapping[sid]['kuid'] = student['login_id'][:6]
            # 'sis_login_id' is a deprecated field according to
            # <https://canvas.instructure.com/doc/api/users.html>.
            elif 'sis_login_id' in student:
                self.mapping[sid]['kuid'] = student['sis_login_id'][:6]

    def publicjson(self):
        return { self.cachename : self.json }

class Submission(cachable.CachableEntity):
    def __init__(self, json = None):
        self.cachename = 'submission'
        if json == None:
            cachable.CachableEntity.__init__(self, self.cachename)
        else:
            self.json = json

        if 'student_ids' in self.json:
            self.student_ids = self.json['student_ids']
        else:
            self.student_ids = [self.json['user_id']]

    def publicjson(self):
        return { self.cachename : self.json }

class Assignment(listed.ListedEntity, cachable.CachableEntity):
    def __init__(self, course, name = None, id = None, path = None):
        self.canvas = course.canvas
        self.course = course
        self.cachename = 'assignment'

        if name == None and id == None:
            if path == None:
                path = '.'
                walk = True
            else:
                walk = False
            cachable.CachableEntity.__init__(self, self.cachename, path, walk)
            listed.ListedEntity.__init__(self)
        else:
            entities = self.canvas.list_assignments(self.course.id)
            listed.ListedEntity.__init__(self, entities, name, id)

        self.subs = list(map(Submission, self.submissions()))

    def publicjson(self):
        return { self.cachename : self.json }

    def submission(self, id):
        return self.canvas.get(
            'courses/{}/assignments/{}/submissions/{}'.format(
                self.course.id, self.id, id))

    def submissions(self):
        return self.canvas.get(
            'courses/{}/assignments/{}/submissions'.format(
                self.course.id, self.id),
            all_pages=True)

    def submissions_download_url(self):
        return self.canvas.submissions_download_url(self.course.id, self.id)

    def give_feedback(self, submission_id, grade, filepaths, message,
        use_post = False):
        self.canvas.give_feedback(
          self.course.id, self.course.displayname,
          self.id, submission_id, grade, filepaths, message, use_post)

def _raise_lookup_file(namestr, lastparent):
    raise LookupError((
            "Couldn't locate a file named {}. " +
            "I have looked for it here and in\n" +
            "parent directories up to, and including {}."
        ).format(
            namestr,
            os.path.abspath(os.path.split(lastparent)[0])))

class Canvas:
    def __init__(self,
                 token=None,
                 account_id=None,
                 api_base='https://absalon.ku.dk/api/v1/'):
        self.api_base = api_base

        if token is None:
            (account_id, token) = files.find_rc()

        self.account_id = account_id
        self.token = token

    def get(self, url_relative, **args):
        return _call_api(self.token, 'GET', self.api_base, url_relative, **args)

    def get_verified_file(self, path, url):
        return urllib.request.urlretrieve(url, filename=path)

    def post(self, url_relative, **args):
        return _call_api(self.token, 'POST', self.api_base, url_relative, **args)

    def put(self, url_relative, **args):
        return _call_api(self.token, 'PUT', self.api_base, url_relative, **args)

    def delete(self, url_relative, **args):
        return _call_api(self.token, 'DELETE', self.api_base, url_relative, **args)

    def course(self, name = None, id = None):
        return Course(self, name, id)

    def courses(self):
        return self.get('courses')

    def get_course(self, course_id):
        return self.get('courses/{}'.format(course_id))

    def course_create(self, name: str, license: str = 'private', is_public: bool = False):
        courses = self.courses()
        for c in courses:
            if name == c['name']:
                raise Exception(
                    "The course {} already exists. YAML dump:\n{}".format(
                        name, yaml.dump(c, default_flow_style=False)))
        return self.post('accounts/6/courses', _arg_list=[
                ('course[name]', name),
                ('course[course_code]', ''),
                ('course[license]', license),
                ('course[is_public]', _api_bool(is_public)),
                ('enroll_me', 'true')
            ])

    def list_sections(self, course_id):
        return self.get('courses/{}/sections'.format(course_id), all_pages=True)

    def create_section(self, course_id, name):
        sections = self.list_sections(course_id)
        existing = [s for s in sections if name == s['name']]
        for s in existing:
            raise Exception(
                "The section {} already exists. YAML dump:\n{}".format(
                    name, yaml.dump(s, default_flow_style=False)))
        _arg_list = [('course_section[name]', name)]
        return self.post('courses/{}/sections'.format(course_id),
            _arg_list=_arg_list)

    def delete_section(self, section_id):
        return self.delete('sections/{}'.format(section_id))

    def section_enroll(self, section_id, user_id):
        _arg_list = [('enrollment[user_id]', user_id)]
        return self.post('sections/{}/enrollments'.format(section_id),
            _arg_list=_arg_list)

    def all_students(self, course_id):
        sections = self.get('courses/{}/sections'.format(course_id),
                            _arg_list=[('include','students')])
        students = []
        for section in sections:
            if 'students' in section:
                students.extend(section['students'])

        return students

    def user(self, user_id):
        return self.get('users/{}/profile'.format(user_id))

    def course_student(self, course_id, user_id):
        user = self.get('courses/{}/users/{}'.format(course_id, user_id))
        return user

    def group_categories(self, course_id):
        return self.get('courses/{}/group_categories'.format(course_id))

    def create_group_category(self, course_id: int, name: str):
        return self.post(
            'courses/{}/group_categories'.format(course_id),
            name=name)

    def list_group_categories(self, course_id: int):
        return self.get(
            'courses/{}/group_categories'.format(course_id),
            all_pages=True)

    def delete_group_category(self, gcat_id: int):
        return self.delete(
            'group_categories/{}'.format(gcat_id))

    ########## group methods ######################
    def groups(self, group_category_id):
        return self.get('group_categories/{}/groups'.format(group_category_id),
                        all_pages=True)
    def groups_in_course(self, course_id):
        return self.get('courses/{}/groups'.format(course_id),
                        all_pages=True)
    def group(self, group_id):
        return self.get('/groups/{}'.format(group_id))

    def group_members(self, group_id):
        return self.get('/groups/{}/users'.format(group_id),
                        all_pages=True)
    ##################################

    def create_group(self, group_category_id, name):
        return self.post('group_categories/{}/groups'.format(group_category_id),
                         name=name, join_level='invitation_only')

    def delete_all_assignment_groups(self, group_category_id):
        groups = self.get('group_categories/{}/groups'.format(group_category_id),
                          all_pages=True)
        group_ids = [g['id'] for g in groups]
        for gid in group_ids:
            self.delete('groups/{}'.format(gid))

    def add_group_members(self, group_id, members):
        args = {
            'members[]': members
        }
        return self.put('groups/{}'.format(group_id), **args)

    def list_assignments(self, course_id):
        return self.get('courses/{}/assignments'.format(course_id))

    def assignment(self, course_id, assignment_id):
        return self.get(
            'courses/{}/assignments/{}'.format(
                course_id, assignment_id))

    def submission_history(self, course_id, assignment_id, student_id):
        args = [
            ('include[]', 'visibility'),
            ('include[]', 'submission_history'),
            ('include[]', 'submission_comments'),
            ('include[]', 'rubric_assessment')
        ]
        url = 'courses/{}/assignments/{}/submissions/{}'.format(
            course_id, assignment_id, student_id)
        return self.get(url, _arg_list=args)

    def submissions_download_url(self, course_id, assignment_id):
        return self.assignment(
            course_id, assignment_id)['submissions_download_url']

    def give_feedback(self,
            course_id, course_name, assignment_id, user_id, grade, message, filepaths,
            use_post = False):

        url_relative = \
            'courses/{}/assignments/{}/submissions/{}'.format(
                course_id, assignment_id, user_id)

        upload = lambda filepath : _upload_submission_comment_file(
            self.token, self.api_base, url_relative, course_name, filepath, use_post)
        ids = list(map(upload, filepaths))

        _arg_list = list(map(lambda x: ("comment[file_ids][]", x), ids))
        _arg_list.append(("comment[text_comment]", message))
        _arg_list.append(("comment[group_comment]", True))
        _arg_list.append(("submission[posted_grade]", grade))

        resp = self.put(url_relative, _arg_list=_arg_list)
        if not 'grade' in resp:
          raise Exception("Canvas response looks weird: {}".format(resp))

        print("Looks good.")
        self.show_verification_urls(course_id, assignment_id, user_id)
        return resp

    def show_verification_urls(self, course_id, assignment_id, user_id):
        speedgrader_url = "https://absalon.ku.dk/courses/{}/gradebook/speed_grader?assignment_id={}#%7B%22student_id%22%3A%22{}%22%7D".format(course_id, assignment_id, user_id)
        gradebook_url = "https://absalon.ku.dk/courses/{}/assignments/{}/submissions/{}/".format(course_id, assignment_id, user_id)

        print("Verification URLs: \n{}\n{}".format(
            speedgrader_url, gradebook_url))

def main(args):
    try:
        method = args[0].upper()
        url = args[1]
        args = args[2:]
        assert len(args) % 2 == 0
        args = [(args[i], args[i + 1]) for i in range(0, len(args), 2)]
    except IndexError:
        print('error: wrong arguments', file=sys.stderr)
        print('usage: canvas.py [GET|POST|PUT] URL [ARG_NAME ARG_VALUE]...',
              file=sys.stderr)
        return 1

    c = Canvas()
    call = {
        'GET': c.get,
        'POST': c.post,
        'PUT': c.put
    }[method]

    output = call(url, _arg_list=args)
    print(format_json(output))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
