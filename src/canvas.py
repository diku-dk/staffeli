#!/usr/bin/env python3

import json
import os
import requests
import sys
import time
import urllib.parse
import urllib.request

from os.path import basename

def format_json(d):
    return json.dumps(d, sort_keys=True, indent=2, ensure_ascii=False)

def _call_api(token, method, api_base, url_relative, **args):
    try:
        args = args['_arg_list']
    except KeyError:
        pass
    query_string = urllib.parse.urlencode(args, safe='[]@', doseq=True).encode('utf-8')
    url = api_base + url_relative
    headers = {
        'Authorization': 'Bearer ' + token
    }
    req = urllib.request.Request(url, data=query_string, method=method,
                                 headers=headers)
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

    while json['upload_status'] != 'ready':
      print("Waiting for Canvas to download it..")
      time.sleep(3)
      json = requests.get(status_url, headers=headers).json()

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
        all_names = [entity[attr] for entity in entities]
        raise LookupError(
            "No candidate for \"{}\". Your options include {}.".format(
            key, _ppnames(all_names)))

    return matches[0]

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


class Course(NamedEntity):
    def __init__(self, canvas, name = None, id = None):
        self.canvas = canvas

        entities = self.canvas.courses()
        NamedEntity.__init__(self, entities, name, id)

    def assignment(self, name = None, id = None):
        return Assignment(self.canvas, self, name, id)

class Assignment(NamedEntity):
    def __init__(self, canvas, course, name = None, id = None):
        self.canvas = canvas
        self.course = course

        entities = self.canvas.list_assignments(self.course.id)
        NamedEntity.__init__(self, entities, name, id)

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

class Canvas:
    def __init__(self,
                 token=None,
                 api_base='https://absalon.ku.dk/api/v1/'):
        self.api_base = api_base

        if token is None:
            with open('token') as f:
                token = f.read().strip()
        self.token = token

    def get(self, url_relative, **args):
        return _call_api(self.token, 'GET', self.api_base, url_relative, **args)

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

    def all_students(self, course_id):
        sections = self.get('courses/{}/sections'.format(course_id),
                            include='students')
        students = sections[0]['students'] # This only works if there's one
                                           # group for all students, like in the
                                           # typical "Hold 01" case.
        return students

    def course_student(self, course_id, user_id):
        user = self.get('courses/{}/users/{}'.format(course_id, user_id))
        return user

    def group_categories(self, course_id):
        return self.get('courses/{}/group_categories'.format(course_id))

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

        _arg_list = {
            "comment[text_comment]" : 'See attached files.',
            "comment[group_comment]" : True,
            "comment[file_ids][]" : ids,
            "submission[posted_grade]" : grade
        }

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
