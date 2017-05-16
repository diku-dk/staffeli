from hypothesis import given
from staffeli.typed_canvas import Canvas
from typing import Any

from test_common import gen_nonempty_name
from test_common import canvas  # noqa: F401


def is_valid_course(course: Any) -> bool:
    return \
        isinstance(course, dict) and \
        'id' in course and \
        isinstance(course['id'], int) and \
        'name' in course and \
        isinstance(course['name'], str)


@given(name=gen_nonempty_name)  # noqa: F811
def test_create_course(
        name: str,
        canvas: Canvas) -> None:

    # Try and add the given course.
    course = canvas.create_course(name)
    assert is_valid_course(course)
    assert course['name'] == name
