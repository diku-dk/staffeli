import json
import urllib
import urllib.parse
import urllib.request

from typing import Any, BinaryIO, List, Optional, Tuple, Union
from urllib.request import Request
from http.client import HTTPResponse

from staffeli import files

QueryArg = Union[int, str]


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


def _api(
        token: str, method: str, url: str,
        **args: QueryArg) -> Any:
    req = _req(token, method, url, **args)
    with urllib.request.urlopen(req) as f:
        assert isinstance(f, HTTPResponse)
        return _read_json(f)


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


class Canvas:
    def __init__(
        self,
        token: Optional[str]=None,
        account_id: Optional[int]=None,
        api_base: str='https://absalon.ku.dk/api/v1/'
            ) -> None:

        self.api_base = api_base

        if token is None or account_id is None:
            self.account_id, self.token = files.find_rc()
        else:
            self.account_id = account_id  # type: int
            self.token = token  # type: str

    def url(self, rel_url: str) -> str:
        return self.api_base + rel_url

    def get_list(self, rel_url: str, **args: QueryArg) -> List[Any]:
        return _list_api(self.token, 'GET', self.url(rel_url), True, **args)

    def post(self, rel_url: str, **args: QueryArg) -> List[Any]:
        return _api(self.token, 'POST', self.url(rel_url), **args)

    def delete(self, rel_url: str, **args: QueryArg) -> List[Any]:
        return _api(self.token, 'DELETE', self.url(rel_url), **args)

    def list_courses(self) -> Any:
        return self.get_list(
            'courses')

    def create_group_category(self, course_id: int, name: str) -> Any:
        return self.post(
            'courses/{}/group_categories'.format(course_id),
            name=name)

    def list_group_categories(self, course_id: int) -> List[Any]:
        return self.get_list(
            'courses/{}/group_categories'.format(course_id))

    def delete_group_category(self, gcat_id: int) -> Any:
        return self.delete(
            'group_categories/{}'.format(gcat_id))
