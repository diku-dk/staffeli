import pytest

from hypothesis import given
from hypothesis.strategies import lists, text
from staffeli.course import Course
from typing import Any, List

name_chr = \
    list(map(chr,
             list(range(ord('A'), ord('Z') + 1)) +
             list(range(ord('a'), ord('z') + 1)) +
             list(range(ord('0'), ord('9') + 1)) +
             list(map(ord, ['_', '-', '+', '/', '&', ' '])) +
             list(map(ord, ['Æ', 'Ø', 'Å', 'æ', 'ø', 'å']))))


@pytest.fixture(scope='session')
def course() -> Course:
    course = Course(name='StaffeliTestBed')
    for gcat in course.list_group_categories():
        course.delete_group_category(gcat['id'])
    assert len(course.list_group_categories()) == 0
    return course


def is_valid_group_category(gcat: Any) -> bool:
    return \
        isinstance(gcat, dict) and \
        'id' in gcat and \
        isinstance(gcat['id'], int) and \
        'name' in gcat and \
        isinstance(gcat['name'], str)


name_gen = text(
    name_chr, min_size=1, max_size=30).filter(
        lambda s: len(s.strip()) > 0)


@given(name=name_gen)
def test_create_group_category(
        name: str,
        course: Course) -> None:

    # Try and add the given group category.
    gcat = course.create_group_category(name)
    assert is_valid_group_category(gcat)
    assert gcat['name'] == name

    # Try and delete the group category created above.
    deleted_gcat = course.delete_group_category(gcat['id'])
    assert is_valid_group_category(deleted_gcat)
    assert deleted_gcat['id'] == gcat['id']

    # Make sure the group categoy was actually deleted.
    assert len(course.list_group_categories()) == 0


@given(
    names=lists(
        name_gen, min_size=1, max_size=30, unique=True)
    )
def test_create_group_categories(
        names: List[str],
        course: Course) -> None:

    len_before = len(course.list_group_categories())

    # Try and add the given number of group categories.
    gcat_ids = []
    for name in names:
        gcat = course.create_group_category(name)
        gcat_ids.append(gcat['id'])
    len_after = len(course.list_group_categories())
    assert len_after - len_before == len(names)

    # Clean-up: Delete the group categories added above.
    for gcat_id in gcat_ids:
        course.delete_group_category(gcat_id)
    assert len(course.list_group_categories()) == len_before
