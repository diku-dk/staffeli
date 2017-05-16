from hypothesis import given
from staffeli.course import Course
from typing import Any, List

from test_common import gen_name, gen_names
from test_common import canvas, course  # noqa: F401


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

    # Make sure the group categoy was actually deleted.
    assert len(course.list_sections()) == 1


@given(names=gen_names)  # noqa: F811
def test_create_sections(
        names: List[str],
        course: Course) -> None:

    len_before = len(course.list_sections())

    # Try and add the given number of sections.
    section_ids = []
    for name in names:
        section = course.create_section(name)
        section_ids.append(section['id'])
    len_after = len(course.list_sections())
    assert len_after - len_before == len(names)

    # Clean-up: Delete the sections created above.
    for section_id in section_ids:
        course.delete_section(section_id)
    assert len(course.list_sections()) == len_before
