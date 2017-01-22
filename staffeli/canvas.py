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

from staffeli import cachable, files, names, upload

def format_json(d):
    return json.dumps(d, sort_keys=True, indent=2, ensure_ascii=False)

def _req(token, method, api_base, url_relative, **args):
    try:
        args = args['_arg_list']
    except KeyError:
        pass
    if type(args) == type({}):
        args = [(v, k) for k, v in args.items()]
    args.append(('per_page', 9000))
    query_string = urllib.parse.urlencode(args, safe='[]@', doseq=True).encode('utf-8')
    url = api_base + url_relative
    headers = {
        'Authorization': 'Bearer ' + token
    }
    return urllib.request.Request(url, data=query_string, method=method,
                                 headers=headers)

def _call_api(token, method, api_base, url_relative, **args):
    req = _req(token, method, api_base, url_relative, **args)
    with urllib.request.urlopen(req) as f:
        data = json.loads(f.read().decode('utf-8'))
    return data

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

def _lookup_id(id, entities):
    for entity in entities:
        if entity['id'] == id:
            return entity

    ids = ["{} ({})".format(entity['id'], entity['name'])
        for entity in entities]
    raise LookupError(
        "No candidate for {}. Your options include {}.".format(
        id, ", ".join(ids)))

def _lookup_name(name, entities):
    id = None
    matches = []

    for entity in entities:
        if name.lower() in entity['name'].lower():
            matches.append(entity)

    if len(matches) > 1:
        matching_names = [match['name'] for match in matches]
        raise LookupError(
            "Multiple candidates for \"{}\": {}.".format(
                name, names.pp(matching_names)))

    if len(matches) == 0:
        all_names = [entity['name'] for entity in entities]
        raise LookupError(
            "No candidate for \"{}\". Your options include {}.".format(
            name, names.pp(all_names)))

    return matches[0]

class ListedEntity:
    def __init__(self, entities = None, name = None, id = None):
        if entities != None:
            if name != None:
                self.json = _lookup_name(name, entities)
            elif id != None:
                self.json = _lookup_id(id, entities)
            else:
                raise LookupError(
                    "For me to find a course, you must provide a name or id.")
        if self.json != None:
            self.id = self.json['id']
            self.displayname = self.json['name']
        else:
            raise TypeError(
                "ListedEntity initialized with insufficient data")

class GroupList(ListedEntity, cachable.CachableEntity):
    def __init__(self, course, path = None, name = None, id = None):
        self.cachename = 'groups'
        self.canvas = course.canvas

        if path != None:
            cachable.CachableEntity.__init__(self, path = path, walk = False)
        else:
            if id != None:
                self.id = id
            else:
                entities = self.canvas.group_categories(course.id)
                ListedEntity.__init__(self, entities, name)

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

class Course(ListedEntity, cachable.CachableEntity):
    def __init__(self, canvas = None, name = None, id = None):

        if canvas == None:
            canvas = Canvas()

        self.canvas = canvas
        self.cachename = 'course'

        if name == None and id == None:
            cachable.CachableEntity.__init__(self)
            ListedEntity.__init__(self)
        else:
            entities = self.canvas.courses()
            ListedEntity.__init__(self, entities, name, id)

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
            cachable.CachableEntity.__init__(self, searchdir)
        else:
            self.json = course.canvas.all_students(course.id)

        self.mapping = {}
        for student in self.json:
            sid = student['id']
            self.mapping[sid] = student
            if not 'sis_login_id' in student:
                continue
            self.mapping[sid]['kuid'] = student['sis_login_id'][:6]

    def publicjson(self):
        return { self.cachename : self.json }

class Submission(cachable.CachableEntity):
    def __init__(self, json = None):
        self.cachename = 'submisison'
        if json == None:
            cachable.CachableEntity.__init__(self)
        else:
            self.json = json

        self.student_ids = [self.json['user_id']]

    def publicjson(self):
        return { self.cachename : self.json }

class Assignment(ListedEntity, cachable.CachableEntity):
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
            cachable.CachableEntity.__init__(self, path = path, walk = walk)
            ListedEntity.__init__(self)
        else:
            entities = self.canvas.list_assignments(self.course.id)
            ListedEntity.__init__(self, entities, name, id)

        self.subs = map(Submission, self.submissions())

    def publicjson(self):
        return { self.cachename : self.json }

    def submissions(self):
        return self.canvas.get(
            'courses/{}/assignments/{}/submissions?per_page=9000'.format(
            self.course.id, self.id))

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
                 api_base='https://absalon.ku.dk/api/v1/'):
        self.api_base = api_base

        if token is None:
            with open(files.find_token_file()) as f:
                token = f.read().strip()
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

    def section_list(self, course_id):
        _arg_list = [('include[]', 'students')]
        return self.get('courses/{}/sections'.format(course_id),
            _arg_list=_arg_list)

    def section_create(self, course_id, name):
        sections = self.section_list(course_id)
        existing = [s for s in sections if name == s['name']]
        for s in existing:
            raise Exception(
                "The section {} already exists. YAML dump:\n{}".format(
                    name, yaml.dump(s, default_flow_style=False)))
        _arg_list = [('course_section[name]', name)]
        return self.post('courses/{}/sections'.format(course_id),
            _arg_list=_arg_list)

    def section_delete(self, section_id):
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

    ########## group methods ######################
    def groups(self, group_category_id):
        return self.get('group_categories/{}/groups'.format(group_category_id),
                          per_page=9000)
    def group(self, group_id):
        return self.get('/groups/{}'.format(group_id))

    def group_members(self, group_id):
        return self.get('/groups/{}/users'.format(group_id),
                          per_page=9000)
    ##################################

    def create_group(self, group_category_id, name):
        return self.post('group_categories/{}/groups'.format(group_category_id),
                         name=name, join_level='invitation_only')

    def delete_all_assignment_groups(self, group_category_id):
        groups = self.get('group_categories/{}/groups'.format(group_category_id),
                          per_page=9000)
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

        speedgrader_url = "https://absalon.ku.dk/courses/{}/gradebook/speed_grader?assignment_id={}#%7B%22student_id%22%3A%22{}%22%7D".format(course_id, assignment_id, user_id)
        gradebook_url = "https://absalon.ku.dk/courses/{}/gradebook/".format(course_id)

        print("Looks good.\nVerification URLs: \n{}\n{}".format(
            speedgrader_url, gradebook_url))
        return resp

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
