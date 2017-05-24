import pytest

from hypothesis import given
from hypothesis.strategies import lists, text
from staffeli.typed_canvas import Canvas
from staffeli.course import Course

from typing import List


name_chr = \
    list(map(chr,
             list(range(ord('A'), ord('Z') + 1)) +
             list(range(ord('a'), ord('z') + 1)) +
             list(range(ord('0'), ord('9') + 1)) +
             list(map(ord, ['_', '-', '+', '/', '&', ' '])) +
             list(map(ord, ['Æ', 'Ø', 'Å', 'æ', 'ø', 'å']))))

pseudonym_chr = \
    list(map(chr,
             list(range(ord('A'), ord('Z') + 1)) +
             list(range(ord('a'), ord('z') + 1))))

gen_name = text(
    name_chr, min_size=1, max_size=30)
gen_names = lists(
    gen_name, min_size=1, max_size=30, unique=True)

gen_nonempty_name = gen_name.filter(lambda s: len(s.strip()) > 0)
gen_nonempty_names = lists(
    gen_nonempty_name, min_size=1, max_size=30, unique=True)

gen_pseudonym = text(
    pseudonym_chr, min_size=1, max_size=30).filter(lambda s: len(s.strip()) > 0)
gen_pseudonyms = lists(
    gen_pseudonym, min_size=1, max_size=30, unique=True)


@pytest.fixture(scope='session')
def canvas() -> Canvas:
    return Canvas(
        token='canvas-docker',
        account_id=1,
        base_url='http://localhost:3000/')


def _create_course_if_missing(canvas: Canvas, name: str) -> None:
    for course in canvas.list_courses():
        if course['name'] == name:
            return
    canvas.create_course(name)


@pytest.fixture(scope='session')
def course_name() -> str:
    return 'StaffeliTestCourse'


@pytest.fixture(scope='session')
def init_course(canvas: Canvas, course_name: str) -> Course:
    _create_course_if_missing(canvas, course_name)
    return Course(canvas=canvas, name=course_name)


def _get_section_or_create(
        init_course: Course,
        name: str
        ) -> int:
    for section in init_course.list_sections():
        if section['name'] == name:
            return section['id']
    return init_course.create_section(name)['id']


@pytest.fixture(scope='session')
def section_name() -> str:
    return 'StaffeliTestSection'


@pytest.fixture(scope='session')
def section_id(
        init_course: Course,
        section_name: str
        ) -> int:
    return _get_section_or_create(init_course, section_name)


@pytest.fixture(scope='session')
def user_id() -> int:
    return 1


@pytest.fixture(scope='session')
def user_ids(
        init_course : Course,
        ) -> List[int]:
    names = gen_pseudonyms.example()
    uids = []
    for name in names:
        u = init_course.canvas.create_user(name)
        uids.append(u['id'])
    return uids


@pytest.fixture(scope='session')
def gcat_ids(
        init_course : Course,
        ) -> List[int]:
    names = gen_nonempty_names.example()
    gcat_ids = []
    for name in names:
        gcat = init_course.canvas.create_group_category(name)
        gcat_ids.append(gcat['id'])
    return gcat_ids


def _get_gcat_or_create(
        init_course: Course,
        name: str
        ) -> int:
    for gcat in init_course.list_group_categories():
        if gcat['name'] == name:
            return gcat['id']
    return init_course.create_group_category(name)['id']


@pytest.fixture(scope='session')
def gcat_name() -> str:
    return 'StaffeliTestGCat'


@pytest.fixture(scope='session')
def gcat_id(
        init_course: Course,
        gcat_name: str
        ) -> int:
    gcat_id = _get_gcat_or_create(init_course, gcat_name)
    for group in init_course.list_groups(gcat_id):
        init_course.delete_group(group['id'])
    return gcat_id
