import pytest

from staffeli.typed_canvas import Canvas


@pytest.fixture(scope='session')
def canvas() -> Canvas:
    return Canvas(
        token='canvas-docker',
        account_id=1,
        base_url='http://localhost:3000/')


def test_no_courses(canvas: Canvas) -> None:
    assert len(canvas.list_courses()) == 0
