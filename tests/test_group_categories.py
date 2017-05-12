import pytest

from hypothesis import given
from hypothesis.strategies import lists, text
from staffeli.canvas import Canvas
from typing import Any, List

name_chr = [chr(c) for c in range(ord('a'), ord('z') + 1)]


@pytest.fixture(scope='session')
def canvas() -> Canvas:
    return Canvas()


@pytest.fixture(scope='session')
def course_id(canvas: Canvas) -> int:
    course_id = canvas.course('StaffeliTestBed').id
    for gcat in canvas.list_group_categories(course_id):
        canvas.delete_group_category(gcat['id'])
    assert len(canvas.list_group_categories(course_id)) == 0
    return course_id


def is_valid_group_category(gcat: Any) -> bool:
    return \
        isinstance(gcat, dict) and \
        'id' in gcat and \
        isinstance(gcat['id'], int) and \
        'name' in gcat and \
        isinstance(gcat['name'], str)


@given(
    name=text(name_chr, min_size=1, max_size=10)
    )
def test_create_group_category(
        name: str,
        canvas: Canvas,
        course_id: int) -> None:

    # Try and add the given group category.
    gcat = canvas.create_group_category(course_id, name)
    assert is_valid_group_category(gcat)
    assert gcat['name'] == name

    # Try and delete the group category created above.
    deleted_gcat = canvas.delete_group_category(gcat['id'])
    assert is_valid_group_category(deleted_gcat)
    assert deleted_gcat['id'] == gcat['id']

    # Make sure the group categoy was actually deleted.
    assert len(canvas.list_group_categories(course_id)) == 0


@given(
    names=lists(
        text(name_chr, min_size=1, max_size=10),
        min_size=1, max_size=10, unique=True)
    )
def test_create_group_categories(
        names: List[str],
        canvas: Canvas,
        course_id: int) -> None:

    len_before = len(canvas.list_group_categories(course_id))

    # Try and add the given number of group categories.
    gcat_ids = []
    for name in names:
        gcat = canvas.create_group_category(course_id, name)
        gcat_ids.append(gcat['id'])
    len_after = len(canvas.list_group_categories(course_id))
    assert len_after - len_before == len(names)

    # Clean-up: Delete the group categories added above.
    for gcat_id in gcat_ids:
        canvas.delete_group_category(gcat_id)
    assert len(canvas.list_group_categories(course_id)) == len_before
