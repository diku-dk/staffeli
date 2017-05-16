from staffeli import listed, cachable
from staffeli.typed_canvas import Canvas

from typing import Any, Optional


class Course(listed.ListedEntity, cachable.CachableEntity):
    canvas = None  # type: Canvas
    id = None  # type: int
    displayname = None  # type: str

    def __init__(
        self,
        canvas: Optional[Canvas]=None,
        name: Optional[str]=None,
        id: Optional[int]=None
            ) -> None:

        if canvas is None:
            self.canvas = Canvas()
        else:
            self.canvas = canvas

        self.cachename = 'course'

        if name is None and id is None:
            cachable.CachableEntity.__init__(self, self.cachename)
            listed.ListedEntity.__init__(self)
        else:
            entities = self.canvas.list_courses()
            listed.ListedEntity.__init__(self, entities, name, id)

        assert isinstance(self.json['id'], int)
        assert isinstance(self.json['name'], str)

        self.id = self.json['id']
        self.displayname = self.json['name']

    def web_url(self) -> str:
        return self.canvas.web_url('courses/{}/'.format(self.id))

    def create_section(self, name: str) -> Any:
        return self.canvas.create_section(self.id, name)

    def list_sections(self) -> Any:
        return self.canvas.list_sections(self.id)

    def delete_section(self, section_id: int) -> Any:
        return self.canvas.delete_section(section_id)

    def section_enroll(self, section_id: int, user_id: int) -> Any:
        return self.canvas.section_enroll(section_id, user_id)

    def create_group_category(self, name: str) -> Any:
        return self.canvas.create_group_category(self.id, name)

    def list_group_categories(self) -> Any:
        return self.canvas.list_group_categories(self.id)

    def delete_group_category(self, gcat_id: int) -> Any:
        return self.canvas.delete_group_category(gcat_id)
