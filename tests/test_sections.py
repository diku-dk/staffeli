import pytest

from hypothesis import given
from hypothesis.strategies import lists, text
from staffeli.canvas import Canvas
from typing import Any, List

name_chr = \
    list(map(chr,
             list(range(ord('A'), ord('Z') + 1)) +
             list(range(ord('a'), ord('z') + 1)) +
             list(range(ord('0'), ord('9') + 1)) +
             list(map(ord, ['_', '-', '+', '/', '&', ' '])) +
             list(map(ord, ['Æ', 'Ø', 'Å', 'æ', 'ø', 'å']))))


@pytest.fixture(scope='session')
def canvas() -> Canvas:
    return Canvas()


@pytest.fixture(scope='session')
def course_id(canvas: Canvas) -> int:
    course_id = canvas.course('StaffeliTestBed').id
    for section in canvas.list_sections(course_id):
        if section['name'] != 'StaffeliTestBed':
            canvas.section_delete(section['id'])
    assert len(canvas.list_sections(course_id)) == 1
    return course_id


def is_valid_section(section: Any) -> bool:
    return \
        isinstance(section, dict) and \
        'id' in section and \
        isinstance(section['id'], int) and \
        'name' in section and \
        isinstance(section['name'], str)


@given(
    name=text(name_chr, min_size=1, max_size=30)
    )
def test_create_section(
        name: str,
        canvas: Canvas,
        course_id: int) -> None:

    # Try and add the given section.
    section = canvas.create_section(course_id, name)
    assert is_valid_section(section)
    assert section['name'] == name

    # Try and delete the section created above.
    deleted_section = canvas.delete_section(section['id'])
    assert is_valid_section(deleted_section)
    assert deleted_section['id'] == section['id']

    # Make sure the group categoy was actually deleted.
    assert len(canvas.list_sections(course_id)) == 1


@given(
    names=lists(
        text(name_chr, min_size=1, max_size=30),
        min_size=1, max_size=30, unique=True)
    )
def test_create_sections(
        names: List[str],
        canvas: Canvas,
        course_id: int) -> None:

    len_before = len(canvas.list_sections(course_id))

    # Try and add the given number of sections.
    section_ids = []
    for name in names:
        section = canvas.create_section(course_id, name)
        section_ids.append(section['id'])
    len_after = len(canvas.list_sections(course_id))
    assert len_after - len_before == len(names)

    # Clean-up: Delete the sections created above.
    for section_id in section_ids:
        canvas.delete_section(section_id)
    assert len(canvas.list_sections(course_id)) == len_before
