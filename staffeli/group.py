from staffeli import listed, cachable
from staffeli.course import Course

from typing import Any, Optional


class Group(listed.ListedEntity, cachable.CachableEntity):
    course = None  # type: Course
    id = None  # type: int
    displayname = None  # type: str

    def __init__(
        self,
        course: Optional[Course]=None,
        name: Optional[str]=None,
        id: Optional[int]=None
            ) -> None:

        if course is None:
            self.course = Course()
        else:
            self.course = course

        self.cachename = 'group'

        if name is None and id is None:
            cachable.CachableEntity.__init__(self, self.cachename)
            listed.ListedEntity.__init__(self)
        else:
            entities = self.course.list_groups()
            listed.ListedEntity.__init__(self, entities, name, id)

        assert isinstance(self.json['id'], int)
        assert isinstance(self.json['name'], str)

        self.id = self.json['id']
        self.displayname = self.json['name']

    def web_url(self) -> str:
        return self.canvas.web_url('courses/{}/'.format(self.id))
