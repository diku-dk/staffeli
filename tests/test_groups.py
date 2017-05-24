import pytest

from hypothesis import given
from staffeli.course import Course
from staffeli.gcat import GroupCategory
from typing import Any, List

from common import gen_nonempty_name, gen_nonempty_names
from common import canvas, init_course  # noqa: F401
from common import gcat_id, user_id  # noqa: F401
from common import user_ids  # noqa: F401
from common import course_name, gcat_name  # noqa: F401


def is_valid_group(group: Any) -> bool:
    return \
        isinstance(group, dict) and \
        'id' in group and \
        isinstance(group['id'], int) and \
        'name' in group and \
        isinstance(group['name'], str)


@pytest.fixture(scope='function')  # noqa: F811
def course(
        init_course: Course,
        user_ids: List[int]
        ) -> Course:
    for user_id in user_ids:
        init_course.canvas.enroll_user(init_course.id, user_id)
    return init_course


@pytest.fixture(scope='function')  # noqa: F811
def gcat(
        init_course: Course,
        gcat_id: int
        ) -> GroupCategory:
    return GroupCategory(init_course, id=gcat_id)


@given(name=gen_nonempty_name)  # noqa: F811
def _test_create_group(
        name: str,
        gcat: GroupCategory
        ) -> None:

    # Try and add the given group.
    group = gcat.create_group(name)
    assert is_valid_group(group)
    assert group['name'] == name

    # Try and delete the group created above.
    deleted_group = gcat.delete_group(group['id'])
    assert is_valid_group(deleted_group)
    assert deleted_group['id'] == group['id']


@given(names=gen_nonempty_names)  # noqa: F811
def _test_create_groups(
        names: List[str],
        gcat: GroupCategory
        ) -> None:

    # Try and add the given number of groups.
    groups = []
    for name in names:
        group = gcat.create_group(name)
        groups.append(group)

    gids = [s['id'] for s in groups]
    gnames = [s['name'] for s in groups]

    assert sorted(gnames) == sorted(names)

    # Clean-up: Delete the groups created above.
    deleted_ids = []
    for gid in gids:
        del_group = gcat.delete_group(gid)
        deleted_ids.append(del_group['id'])
    assert sorted(deleted_ids) == sorted(gids)
