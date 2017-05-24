import pytest

from hypothesis import given
from staffeli.course import Course
from typing import Any, List

from test_common import gen_nonempty_name, gen_nonempty_names
from test_common import course_name, canvas, init_course  # noqa: F401


def is_valid_group_category(gcat: Any) -> bool:
    return \
        isinstance(gcat, dict) and \
        'id' in gcat and \
        isinstance(gcat['id'], int) and \
        'name' in gcat and \
        isinstance(gcat['name'], str)


@pytest.fixture(scope='function')  # noqa: F811
def course(init_course: Course) -> Course:
    for gcat in init_course.list_group_categories():
        init_course.delete_group_category(gcat['id'])
    return init_course


@given(name=gen_nonempty_name)
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


@given(names=gen_nonempty_names)
def test_create_group_categories(
        names: List[str],
        course: Course) -> None:

    # Try and add the given number of group categories.
    gcats = []
    for name in names:
        gcat = course.create_group_category(name)
        gcats.append(gcat)

    gcat_ids = [gcat['id'] for gcat in gcats]
    gcat_names = [gcat['name'] for gcat in gcats]

    assert sorted(gcat_names) == sorted(names)

    # Clean-up: Delete the group categories added above.
    del_gcat_ids = []
    for gcat_id in gcat_ids:
        del_gcat = course.delete_group_category(gcat_id)
        del_gcat_ids.append(del_gcat['id'])
    assert sorted(del_gcat_ids) == sorted(gcat_ids)
