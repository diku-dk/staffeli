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

from os.path import basename

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

def _upload_via_post(token, api_base, url_relative, filepath):

    url = api_base + url_relative
    headers = {
        'Authorization': 'Bearer ' + token
    }

    name = basename(filepath)
    size = os.stat(filepath).st_size

    params = {
        'name'    : name,
        'size'    : size
    }

    resp = requests.post(url, headers=headers, params=params)

    json = resp.json()
    upload_url = json['upload_url']
    params = json['upload_params']
    name = json['file_param']

    with open(filepath, "rb") as f:
        resp = requests.post(
            upload_url, params=params, files=[(name, f)])

    print(resp.status_code)
    print(resp.text)

    return resp

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

def _upload_submission_comment_file(token, api_base, url_relative, course, filepath):
    viaurl = _upload_transit(course, filepath)
    return _upload_via_url(
        token, api_base,
        url_relative + "/comments/files",
        filepath, viaurl)

def _ppnames(names):
    return "\"{}\"".format("\", \"".join(names))

def _raise_lookup_error(key, attr, entities):
    all_names = [entity[attr] for entity in entities]
    raise LookupError(
        "No candidate for \"{}\". Your options include {}.".format(
        key, _ppnames(all_names)))

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
                name, _ppnames(matching_names)))

    if len(matches) == 0:
        all_names = [entity['name'] for entity in entities]
        raise LookupError(
            "No candidate for \"{}\". Your options include {}.".format(
            name, _ppnames(all_names)))

    return matches[0]

def _find_staffeli_yml(cachename, searchdir = "."):
    parent = searchdir
    namestr = ".staffeli.yml"
    for i in range(9):
        path = _find_file(namestr, parent)
        with open(path, 'r') as f:
            model = yaml.load(f)
        if len(model) == 1 and cachename in model:
            return model
        parent = os.path.join(os.path.split(path)[0], "..")

    _raise_lookup_file(namestr, parent)

class CachedEntity:
    def __init__(self, searchdir = "."):
        model = _find_staffeli_yml(self.cachename, searchdir)
        self.json = model[self.cachename]

    def cache(self, path = None):
        if os.path.isdir(path):
            path = os.path.join(path, ".staffeli.yml")
        with open(path, 'w') as f:
            yaml.dump(self.publicjson(),
                f, default_flow_style=False, encoding='utf-8')

    def publicjson(self):
        return self.json

class NamedEntity:
    def __init__(self, entities, name = None, id = None):
        if name != None:
            self.json = _lookup_name(name, entities)
        elif id != None:
            self.json = _lookup_id(id, entities)
        else:
            raise LookupError(
                "For me to find a course, you must provide a name or id.")

        self.id = self.json['id']
        self.displayname = self.json['name']

class GroupList(NamedEntity, CachedEntity):
    def __init__(self, course, name = None, id = None):
        self.canvas = course.canvas
        if id != None:
            self.id = id
        else:
            entities = self.canvas.group_categories(course.id)
            NamedEntity.__init__(self, entities, name)
            self.name = self.json['name']

        self.json = self.canvas.groups(self.id)
        for group in self.json:
            group['members'] = self.canvas.group_members(group['id'])


class GroupCategoryList(CachedEntity):
    def __init__(self, canvas, course_id):
        self.json = canvas.group_categories(course_id)

    def publicjson(self):
        json = copy.deepcopy(self.json)
        for cat in json:
            del cat['is_member']
        return { 'group_categories': json }

class Course(NamedEntity, CachedEntity):
    def __init__(self, canvas = None, name = None, id = None):

        if canvas == None:
            canvas = Canvas()

        self.canvas = canvas
        self.cachename = 'course'

        if name == None and id == None:
            CachedEntity.__init__(self)
        else:
            entities = self.canvas.courses()
            NamedEntity.__init__(self, entities, name, id)

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

class StudentList(CachedEntity):
    def __init__(self, course):
        self.canvas = course.canvas
        self.course = course
        self.json = self.canvas.all_students(course.id)
        self.cachename = 'students'

    def publicjson(self):
        return { self.cachename : json }

class Assignment(NamedEntity, CachedEntity):
    def __init__(self, course, name = None, id = None):
        self.canvas = course.canvas
        self.course = course
        self.cachename = 'assignment'

        entities = self.canvas.list_assignments(self.course.id)
        NamedEntity.__init__(self, entities, name, id)

        self.json['submissions'] = self.submissions()

    def publicjson(self):
        return { self.cachename : self.json }

    def submissions(self):
        return self.canvas.get(
            'courses/{}/assignments/{}/submissions?per_page=9000'.format(
            self.course.id, self.id))

    def submissions_download_url(self):
        return self.canvas.submissions_download_url(self.course.id, self.id)

    def give_feedback(self, submission_id, grade, filepaths):
        self.canvas.give_feedback(
          self.course.id, self.course.displayname,
          self.id, submission_id, grade, filepaths)

def _raise_lookup_file(namestr, lastparent):
    raise LookupError((
            "Couldn't locate a file named {}. " +
            "I have looked for it here and in\n" +
            "parent directories up to, and including {}."
        ).format(
            namestr,
            os.path.abspath(os.path.split(lastparent)[0])))

def _find_file(cs, parent = "."):
    if type(cs) == type(""):
        cs = [cs]

    for i in range(9):
        for c in cs:
            path = os.path.join(parent, c)
            if os.path.isfile(path):
                return path
        parent = os.path.join("..", parent)

    if len(cs) == 1:
        namestr = cs[0]
    elif len(cs) == 2:
        namestr = "either {} or {}".format(cs[0], cs[1])
    else:
        namestr = "either {}, or {}".format(", ".join(cs[:-1]), cs[-1])

    _raise_lookup_file(namestr, parent)

def _find_token_file():
    return _find_file([ "token", "token.txt", ".token" ])

class Canvas:
    def __init__(self,
                 token=None,
                 api_base='https://absalon.ku.dk/api/v1/'):
        self.api_base = api_base

        if token is None:
            with open(_find_token_file()) as f:
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
            course_id, course_name, assignment_id, user_id, grade, filepaths):

        url_relative = \
            'courses/{}/assignments/{}/submissions/{}'.format(
                course_id, assignment_id, user_id)

        upload = lambda filepath : _upload_submission_comment_file(
            self.token, self.api_base, url_relative, course_name, filepath)
        ids = list(map(upload, filepaths))

        _arg_list = list(map(lambda x: ("comment[file_ids][]", x), ids))
        _arg_list.append(("comment[text_comment]", 'See attached files.'))
        _arg_list.append(("comment[group_comment]", True))
        _arg_list.append(("submission[posted_grade]", grade))

        resp = self.put(url_relative, _arg_list=_arg_list)
        if not 'grade' in resp:
          raise Exception("Canvas response looks weird: {}".format(resp))

        speedgrader_url = "https://absalon.ku.dk/courses/{}/gradebook/speed_grader?assignment_id={}#%7B%22student_id%22%3A%22{}%22%7D".format(course_id, assignment_id, user_id)

        print("Looks good.\nVerification URL: " + speedgrader_url)
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
