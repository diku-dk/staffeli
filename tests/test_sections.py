from hypothesis import given
from staffeli.course import Course
from typing import Any, List

from test_common import gen_name, gen_names
from test_common import canvas, course  # noqa: F401
from test_common import section_id, user_id  # noqa: F401


def is_valid_section(section: Any) -> bool:
    return \
        isinstance(section, dict) and \
        'id' in section and \
        isinstance(section['id'], int) and \
        'name' in section and \
        isinstance(section['name'], str)


@given(name=gen_name)  # noqa: F811
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


@given(names=gen_names)  # noqa: F811
def test_create_sections(
        names: List[str],
        course: Course) -> None:

    len_before = len(course.list_sections())

    # Try and add the given number of sections.
    sids = []
    for name in names:
        section = course.create_section(name)
        sids.append(section['id'])
    len_after = len(course.list_sections())
    assert len_after - len_before == len(names)

    # Clean-up: Delete the sections created above.
    for sid in sids:
        course.delete_section(sid)
    assert len(course.list_sections()) == len_before
