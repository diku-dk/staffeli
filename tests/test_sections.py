import pytest

from hypothesis import given
from hypothesis.strategies import lists, text
from staffeli.canvas import Canvas
from typing import List

name_chr = [chr(c) for c in range(ord('a'), ord('z') + 1)]


@pytest.fixture(scope='session')
def canvas() -> Canvas:
    return Canvas()


@pytest.fixture(scope='session')
def course_id(canvas: Canvas) -> int:
    return canvas.course('StaffeliTestBed').id


@given(
    names=lists(
        text(name_chr, min_size=1, max_size=10),
        min_size=1, max_size=10, unique=True)
    )
def test_section_create(
        names: List[str],
        canvas: Canvas,
        course_id: int) -> None:

    len_before = len(canvas.section_list(course_id))

    assert len_before == 1

    sids = []
    for name in names:
        s = canvas.section_create(course_id, name)
        sids.append(s['id'])

    len_after = len(canvas.section_list(course_id))

    assert len_after - len_before == len(names)

    for sid in sids:
        canvas.section_delete(sid)

    len_finally = len(canvas.section_list(course_id))

    assert len_finally == 1
