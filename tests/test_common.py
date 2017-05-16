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

gen_name = text(name_chr, min_size=1, max_size=30)
gen_names = lists(
    gen_name, min_size=1, max_size=30, unique=True)


@pytest.fixture(scope='session')
def canvas() -> Canvas:
    return Canvas(
        token='canvas-docker',
        account_id=1,
        base_url='http://localhost:3000/')


@pytest.fixture(scope='session')
def course(canvas: Canvas) -> Course:
    canvas.create_course('StaffeliTestBed')
    return Course(canvas=canvas, name='StaffeliTestBed')
