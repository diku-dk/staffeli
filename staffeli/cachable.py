import os.path
import yaml
from staffeli import files

from typing import Any


class CachableEntity:
    cachename = None  # type: str

    def __init__(
            self, cachename: str,
            path: str = '.', walk: bool = True
            ) -> None:
        if os.path.isdir(path):
            depth = [i for i in [1] if not walk]
            self.parentdir, model = files.find_staffeli_file(
                cachename, path, *depth)
        elif os.path.isfile(path):
            self.parentdir = os.path.split(path)[0]
            model = files.load_staffeli_file(path)
        else:
            raise LookupError((
                "{} is neither a directory, nor file path."
                ).format(path))
        self.json = model[cachename]

    def cache(self, path: str) -> None:
        if os.path.isdir(path):
            path = os.path.join(path, ".staffeli.yml")
        with open(path, 'w') as f:
            yaml.dump(
                self.publicjson(),
                f, default_flow_style=False, encoding='utf-8')

    def publicjson(self) -> Any:
        return self.json
