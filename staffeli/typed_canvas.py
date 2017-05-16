import json
import urllib
import urllib.parse
import urllib.request

from typing import Dict  # noqa: F401
from typing import Any, BinaryIO, List, Optional, Tuple, Union
from urllib.request import Request
from http.client import HTTPResponse

from staffeli import files

QueryArg = Union[int, str]


def _req(token: str, method: str, url: str, **args: QueryArg) -> Request:
    """The root of staffeli: Perform an API request.

    Handle with care."""
    query_string = urllib.parse.urlencode(
        list(args.items()),
        safe='[]@', doseq=True).encode('utf-8')

    headers = {'Authorization': 'Bearer ' + token}

    return urllib.request.Request(
        url, data=query_string, method=method, headers=headers)


def _read_json(f: Union[HTTPResponse, BinaryIO]) -> Any:
    return json.loads(f.read().decode('utf-8'))


def _list_req(token: str, method: str, url: str, **args: QueryArg) -> Request:
    # In the case of list-returning API calls, maximize the number of entries
    # returned.  100 appears to be the max in at least one instance.
    args['per_page'] = 100
    return _req(token, method, url, **args)


def _parse_pagination_link(s: str) -> Tuple[str, str]:
    link, rel = s.split('; rel="')
    link = link[1:-1]
    rel = rel[:-1]
    return (rel, link)


def _api(
        token: str, method: str, url: str,
        **args: QueryArg) -> Any:
    req = _req(token, method, url, **args)
    with urllib.request.urlopen(req) as f:
        assert isinstance(f, HTTPResponse)
        return _read_json(f)


def _list_api(
        token: str, method: str, url: str,
        **args: QueryArg) -> List[Any]:
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
            messages = str(f.getheader('Link')).split(',')
            links = [_parse_pagination_link(m) for m in messages]
            pagination_links = {rel: link for rel, link in links}
            if pagination_links['current'] == pagination_links['last']:
                break
            else:
                url = pagination_links['next']
                req = _list_req(token, method, url, **args)
    return entries


def _api_bool(value: bool) -> int:
    if value:
        return 1
    else:
        return 0


class Canvas:
    base_url = None  # type: str
    api_base = None  # type: str

    def __init__(
        self,
        token: Optional[str]=None,
        account_id: Optional[int]=None,
        base_url: str='https://absalon.ku.dk/',
        api_base: str='api/v1/'
            ) -> None:

        self.base_url = base_url
        self.api_base = api_base

        if token is None or account_id is None:
            self.account_id, self.token = files.find_rc()
        else:
            self.account_id = account_id  # type: int
            self.token = token  # type: str

    def api_url(self, rel_url: str) -> str:
        return self.base_url + self.api_base + rel_url

    def web_url(self, rel_url: str) -> str:
        return self.base_url + rel_url

    def get_list(self, rel_url: str, **args: QueryArg) -> List[Any]:
        return _list_api(self.token, 'GET', self.api_url(rel_url), **args)

    def post(self, rel_url: str, **args: QueryArg) -> List[Any]:
        return _api(self.token, 'POST', self.api_url(rel_url), **args)

    def delete(self, rel_url: str, **args: QueryArg) -> List[Any]:
        return _api(self.token, 'DELETE', self.api_url(rel_url), **args)

    def list_courses(self) -> List[Any]:
        url = 'courses'
        return self.get_list(url)

    def create_course(
            self,
            name: str,
            license: str = 'private',
            is_public: bool = False) -> Any:
        url = 'accounts/{}/courses'.format(self.account_id)
        args = {
            'course[name]': name,
            'course[course_code]': '',
            'course[license]': license,
            'course[is_public]': _api_bool(is_public),
            'enroll_me': 'true'
        }  # type: Dict[str, Union[int, str]]
        return self.post(url, **args)

    def list_sections(self, course_id: int) -> List[Any]:
        url = 'courses/{}/sections'.format(course_id)
        return self.get_list(url)

    def create_section(self, course_id: int, name: str) -> Any:
        url = 'courses/{}/sections'.format(course_id)
        args = {'course_section[name]': name}
        return self.post(url, **args)

    def delete_section(self, section_id: int) -> Any:
        """Delete a section.

        Note how this method does not take a course ID.
        Section IDs are global across all courses, and,
        to our knowledge, are not instantly re-usable."""
        url = 'sections/{}'.format(section_id)
        return self.delete(url)

    def section_enroll(self, section_id: int, user_id: int) -> Any:
        url = 'sections/{}/enrollments'.format(section_id)
        args = {'enrollment[user_id]': user_id}
        return self.post(url, **args)

    def create_group_category(self, course_id: int, name: str) -> Any:
        url = 'courses/{}/group_categories'.format(course_id)
        args = {'name': name}
        return self.post(url, **args)

    def list_group_categories(self, course_id: int) -> List[Any]:
        url = 'courses/{}/group_categories'.format(course_id)
        return self.get_list(url)

    def delete_group_category(self, gcat_id: int) -> Any:
        """Delete a group category.

        Note how this method does not take a course ID.
        Group Category IDs are global across all courses, and,
        to our knowledge, are not instantly re-usable."""
        url = 'group_categories/{}'.format(gcat_id)
        return self.delete(url)
