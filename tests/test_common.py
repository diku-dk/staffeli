import pytest

from hypothesis.strategies import lists, text
from staffeli.typed_canvas import Canvas
from staffeli.course import Course


name_chr = \
    list(map(chr,
             list(range(ord('A'), ord('Z') + 1)) +
             list(range(ord('a'), ord('z') + 1)) +
             list(range(ord('0'), ord('9') + 1)) +
             list(map(ord, ['_', '-', '+', '/', '&', ' '])) +
             list(map(ord, ['Æ', 'Ø', 'Å', 'æ', 'ø', 'å']))))

gen_name = text(
    name_chr, min_size=1, max_size=30)
gen_names = lists(
    gen_name, min_size=1, max_size=30, unique=True)

gen_nonempty_name = gen_name.filter(lambda s: len(s.strip()) > 0)
gen_nonempty_names = lists(
    gen_nonempty_name, min_size=1, max_size=30, unique=True)


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
def course(canvas: Canvas) -> Course:
    name = 'StaffeliTestBed'
    _create_course_if_missing(canvas, name)
    return Course(canvas=canvas, name=name)
