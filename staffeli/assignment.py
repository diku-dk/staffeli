from staffeli import cachable
from staffeli.canvas import Course
from staffeli.listed import ListedEntity
from staffeli.submission import Submission

from typing import Any, Dict, Optional


class Assignment(ListedEntity, cachable.CachableEntity):
    def __init__(
            self, course: Course,
            name: Optional[str] = None,
            id: Optional[int] = None,
            path: Optional[str] = None) -> None:
        self.canvas = course.canvas
        self.course = course
        self.cachename = 'assignment'

        if name is None and id is None:
            if path is None:
                path = '.'
                walk = True
            else:
                walk = False
            cachable.CachableEntity.__init__(self, self.cachename, path, walk)
            ListedEntity.__init__(self)
        else:
            entities = self.canvas.list_assignments(self.course.id)
            ListedEntity.__init__(self, entities, name, id)

        self.subs = map(Submission, self.submissions())

    def publicjson(self) -> Dict[str, Any]:
        return {self.cachename: self.json}

    def submissions(self):
        return self.canvas.get(
            'courses/{}/assignments/{}/submissions?per_page=9000'.format(
                self.course.id, self.id))

    def submissions_download_url(self):
        return self.canvas.submissions_download_url(self.course.id, self.id)

    def give_feedback(self, submission_id, grade, filepaths, message,
                      use_post=False):
        self.canvas.give_feedback(
          self.course.id, self.course.displayname,
          self.id, submission_id, grade, filepaths, message, use_post)
