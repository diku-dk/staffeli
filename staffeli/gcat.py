from staffeli import listed, cachable
from staffeli.course import Course

from typing import Any, Optional


class GroupCategory(listed.ListedEntity, cachable.CachableEntity):
    course = None  # type: Course
    id = None  # type: int
    displayname = None  # type: str

    def __init__(
        self,
        course: Optional[Course] = None,
        name: Optional[str] = None,
        id: Optional[int] = None
            ) -> None:

        if course is None:
            self.course = Course()
        else:
            self.course = course

        self.cachename = 'gcat'

        if name is None and id is None:
            cachable.CachableEntity.__init__(self, self.cachename)
            listed.ListedEntity.__init__(self)
        else:
            entities = self.course.list_group_categories()
            listed.ListedEntity.__init__(self, entities, name, id)

        assert isinstance(self.json['id'], int)
        assert isinstance(self.json['name'], str)

        self.id = self.json['id']
        self.displayname = self.json['name']

    def web_url(self) -> str:
        return self.course.canvas.web_url(
            'courses/{}/groups#tab-{}'.format(self.course.id, self.id))

    def list_groups(self) -> Any:
        return self.course.list_groups(self.id)

    def create_group(self, name: str) -> Any:
        return self.course.create_group(self.id, name)

    def delete_group(self, group_id: int) -> Any:
        return self.course.delete_group(group_id)
