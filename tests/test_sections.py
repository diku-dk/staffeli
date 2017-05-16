import pytest

from hypothesis import given
from staffeli.course import Course
from typing import Any, List

from test_common import gen_name, gen_names
from test_common import canvas, init_course  # noqa: F401
from test_common import section_id, user_id  # noqa: F401
from test_common import course_name, section_name  # noqa: F401


def is_valid_section(section: Any) -> bool:
    return \
        isinstance(section, dict) and \
        'id' in section and \
        isinstance(section['id'], int) and \
        'name' in section and \
        isinstance(section['name'], str)


@pytest.fixture(scope='function')  # noqa: F811
def course(
        init_course: Course,
        course_name: str,
        section_name: str) -> Course:
    reserved = [course_name, section_name]
    for section in init_course.list_sections():
        if section['name'] in reserved:
            continue
        init_course.delete_section(section['id'])
    return init_course


@given(name=gen_name)
def test_create_section(
        name: str,
        course: Course) -> None:

    # Try and add the given section.
    section = course.create_section(name)
    assert is_valid_section(section)
    assert section['name'] == name

    # Try and delete the section created above.
    deleted_section = course.delete_section(section['id'])
    assert is_valid_section(deleted_section)
    assert deleted_section['id'] == section['id']


def test_enroll_user(  # noqa: F811
        course: Course,
        section_id: int,
        user_id: int) -> None:
    return course.section_enroll(section_id, user_id)


@given(names=gen_names)
def test_create_sections(
        names: List[str],
        course: Course) -> None:

    # Try and add the given number of sections.
    sections = []
    for name in names:
        section = course.create_section(name)
        sections.append(section)

    sids = [s['id'] for s in sections]
    snames = [s['name'] for s in sections]

    assert sorted(snames) == sorted(names)

    # Clean-up: Delete the sections created above.
    deleted_ids = []
    for sid in sids:
        del_section = course.delete_section(sid)
        deleted_ids.append(del_section['id'])
    assert sorted(deleted_ids) == sorted(sids)
