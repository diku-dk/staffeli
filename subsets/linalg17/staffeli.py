#!/usr/bin/env python3

# Copyright 2016-2017 DIKU, DIKUNIX
# Licensed under the EUPL v.1.1 only (the "Licence");
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# http://ec.europa.eu/idabc/eupl.html
# or
# https://web.archive.org/web/20160822183947/http://ec.europa.eu/idabc/eupl.html
# or see it verbatim in LICENSE.md.

import configparser
import json
import os
import os.path
import sys
import urllib
import urllib.parse
import urllib.request

from typing import Any, BinaryIO, Dict, List, Tuple, Union
from urllib.request import Request, urlretrieve
from http.client import HTTPResponse

RC_FILE = os.path.join(os.path.expanduser('~'), '.staffelirc')
RC_SECTION = 'linalg'

API_BASE = "https://absalon.ku.dk/api/v1/"


QueryArg = Union[int, str]


def _get_rc() -> Tuple[str, int]:
    config = configparser.ConfigParser()
    config.read_file(open(RC_FILE))
    section = config[RC_SECTION]
    return (section['token'], int(section['course_id']))


def _url(relative_url: str) -> str:
    return API_BASE + relative_url


def _req(token: str, method: str, url: str, **args: QueryArg) -> Request:
    query_string = urllib.parse.urlencode(
        list(args.items()),
        safe='[]@', doseq=True).encode('utf-8')

    headers = {'Authorization': 'Bearer ' + token}

    print(url)
    return urllib.request.Request(
        url, data=query_string, method=method, headers=headers)


def _read_json(f: Union[HTTPResponse, BinaryIO]) -> Any:
    return json.loads(f.read().decode('utf-8'))


def _list_req(token: str, method: str, url: str, **args: QueryArg) -> Request:
    # In the case of list-returning API calls, maximize the number of entries
    # returned.  100 appears to be the max in at least one instance.  Combine
    # this with the 'all_pages=True' argument in calling '_list_api'.
    args['per_page'] = 100
    return _req(token, method, url, **args)


def _parse_pagination_link(s: str) -> Tuple[str, str]:
    link, rel = s.split('; rel="')
    link = link[1:-1]
    rel = rel[:-1]
    return (rel, link)


def _list_api(
        token: str, method: str, url: str,
        all_pages: bool = True, **args: QueryArg) -> List[Any]:
    req = _list_req(token, method, url, **args)
    entries = []  # type: List[Any]
    while True:
        with urllib.request.urlopen(req) as f:
            assert isinstance(f, HTTPResponse)

            data = _read_json(f)
            if type(data) is list:
                entries.extend(data)
            else:
                entries.append(data)

            # In some cases we want to extract many entries, e.g. the students
            # in a course.  However, some Absalon instances set a per_page
            # limit to 100, so we cannot just set per_page to 9000 and hope
            # for the best.  Instead we utilize the API's pagination facilities
            # documented at
            # <https://canvas.instructure.com/doc/api/file.pagination.html>.
            # This works, although it is not foolproof in the extreme case that
            # entries are added or removed from Absalon between our requests.
            # This is probably not something to worry about.
            if all_pages:
                messages = str(f.getheader('Link')).split(',')
                links = [_parse_pagination_link(m) for m in messages]
                pagination_links = {rel: link for rel, link in links}
                if pagination_links['current'] == pagination_links['last']:
                    break
                else:
                    url = pagination_links['next']
                    req = _list_req(token, method, url, **args)
            else:
                break
    return entries


(TOKEN, COURSE_ID) = _get_rc()


def _get_list(relative_url: str, **args: QueryArg) -> List[Any]:
    return _list_api(TOKEN, 'GET', _url(relative_url), True, **args)


def _get_sections() -> Tuple[Dict[str, int], Dict[int, Any]]:
    results = _get_list(
        "courses/{}/sections".format(COURSE_ID),
        include='students')
    sections = {r['name']: r['id'] for r in results}
    students = {}  # type: Dict[int, Any]
    for r in results:
        for s in r['students']:
            s['section'] = r['name']
            students[s['id']] = s
    return (sections, students)


def _get_assignments() -> Dict[str, int]:
    results = _get_list(
        "courses/{}/assignments".format(COURSE_ID))
    return {r['name']: r['id'] for r in results}


def _get_submissions(assignment_id: int) -> Dict[int, Any]:
    results = _get_list(
        "courses/{}/assignments/{}/submissions".format(
            COURSE_ID, assignment_id))
    return {r['user_id']: r for r in results}


def _normalize_pathname(pathname: str) -> str:
    return pathname.replace(os.sep, '_')


def _mkdir(path: str) -> None:
    if not os.path.isdir(path):
        os.mkdir(path)


def _pp_list(values: List[str]) -> str:
    return "\n * \"{}\"".format("\",\n * \"".join(values))


def _find_key(keys: List[str], needle: str) -> str:
    candidates = []
    lower_needle = needle.lower()
    for key in keys:
        if lower_needle in key.lower():
            candidates.append(key)
    if len(candidates) > 1:
        raise LookupError(
            "Multiple candidates for \"{}\": {}".format(
                needle, _pp_list(candidates)))
    elif len(candidates) == 0:
        raise LookupError(
            "No candidate for \"{}\". Your options include: {}.".format(
                needle, _pp_list(keys)))
    return candidates[0]


def _write_name(path: str, student: Dict[str, Any]) -> None:
    name_path = os.path.join(path, 'name.txt')
    with open(name_path, 'w') as f:
        print(student['name'], file=f)
        print(student['sortable_name'], file=f)


def _fetch_attachments(
        path: str,
        attachments: List[Dict[str, Any]]
        ) -> None:
    for att in attachments:
        targetpath = os.path.join(path, att['filename'])
        print("Downloading {}..".format(targetpath))
        if os.path.isfile(targetpath):
            print("Skipped. Looks like it is already here.")
            # TODO: Do this smarter
            continue
        urlretrieve(att['url'], targetpath)


ASSIGNMENT = _normalize_pathname(sys.argv[1])

sections, students = _get_sections()
assignments = _get_assignments()

assignment_id = assignments[_find_key(list(assignments.keys()), ASSIGNMENT)]

_mkdir(ASSIGNMENT)
for section in sections.keys():
    pathname = _normalize_pathname(section)
    _mkdir(os.path.join(ASSIGNMENT, pathname))

submissions = _get_submissions(assignment_id)
for user_id, sub in submissions.items():
    student = students[user_id]
    kuid = student['login_id'][:6]
    section = student['section']
    pathname = kuid + '_' + str(user_id)
    path = os.path.join(ASSIGNMENT, section, pathname)
    _mkdir(path)
    _write_name(path, student)
    if sub['submission_type'] is None:
        print(
            path,
            "looks like an empty submission :-/ see also the following URL:")
        print(' ', sub['preview_url'])
        continue
    _fetch_attachments(path, sub['attachments'])
