import pytest

from hypothesis import given
from staffeli.course import Course
from typing import Any, List

from test_common import gen_nonempty_name, gen_nonempty_names
from test_common import canvas, init_course  # noqa: F401
from test_common import gcat_id, user_id  # noqa: F401
from test_common import course_name, gcat_name  # noqa: F401


def is_valid_group(group: Any) -> bool:
    return \
        isinstance(group, dict) and \
        'id' in group and \
        isinstance(group['id'], int) and \
        'name' in group and \
        isinstance(group['name'], str)


@pytest.fixture(scope='function')  # noqa: F811
def course(
        init_course: Course
        ) -> Course:
    return init_course


@given(name=gen_nonempty_name)  # noqa: F811
def test_create_group(
        name: str,
        course: Course,
        gcat_id: int
        ) -> None:

    # Try and add the given group.
    group = course.canvas.create_group(gcat_id, name)
    assert is_valid_group(group)
    assert group['name'] == name

    # Try and delete the group created above.
    deleted_group = course.canvas.delete_group(group['id'])
    assert is_valid_group(deleted_group)
    assert deleted_group['id'] == group['id']


@given(names=gen_nonempty_names)  # noqa: F811
def test_create_groups(
        names: List[str],
        course: Course,
        gcat_id: int
        ) -> None:

    # Try and add the given number of groups.
    groups = []
    for name in names:
        group = course.create_group(gcat_id, name)
        groups.append(group)

    gids = [s['id'] for s in groups]
    gnames = [s['name'] for s in groups]

    assert sorted(gnames) == sorted(names)

    # Clean-up: Delete the groups created above.
    deleted_ids = []
    for gid in gids:
        del_group = course.delete_group(gid)
        deleted_ids.append(del_group['id'])
    assert sorted(deleted_ids) == sorted(gids)
