import os
import os.path
import yaml
from typing import Any, Dict, List, Union, Tuple
from staffeli import names

STAFFELI_FILENAME = ".staffeli.yml"
TOKEN_FILENAMES = ["token", "token.txt", ".token"]
STAFFELI_RC = ".staffelirc"
MAX_DIR_SEARCH_DEPTH = 9


def _raise_lookup_error(key, attr, entities):
    all_names = [entity[attr] for entity in entities]
    raise LookupError(
        "No candidate for \"{}\". Your options include {}.".format(
            key, names.pp(all_names)))


def _raise_lookup_file(namestr, lastparent):
    raise LookupError((
            "Couldn't locate a file named {}. " +
            "I have looked for it here and in\n" +
            "parent directories up to, and including {}."
        ).format(
            namestr,
            os.path.abspath(os.path.split(lastparent)[0])))


def _find_file(
        candidate_names, parent='.', max_depth=MAX_DIR_SEARCH_DEPTH):
    if isinstance(candidate_names, str):
        candidate_names = [candidate_names]

    for i in range(MAX_DIR_SEARCH_DEPTH):
        for name in candidate_names:
            path = os.path.join(parent, name)
            if os.path.isfile(path):
                return path
        parent = os.path.join(parent, '..')

    if len(candidate_names) == 1:
        namestr = candidate_names[0]
    elif len(candidate_names) == 2:
        namestr = "either {} or {}".format(
            candidate_names[0], candidate_names[1])
    else:
        namestr = "either {}, or {}".format(
            ", ".join(candidate_names[:-1]), candidate_names[-1])

    _raise_lookup_file(namestr, parent)


def find_token_file():
    return _find_file(TOKEN_FILENAMES)


def find_rc() -> Tuple[int, str]:
    try:
        rcfile = _find_file(STAFFELI_RC)
        import configparser
        config = configparser.ConfigParser()
        config.readfp(open(rcfile))
        config = config['default']
        return (int(config['account_id']), str(config['token']))
    except LookupError:
        with open(_find_file(TOKEN_FILENAMES)) as f:
            token = f.read().strip()
        return (6, token)


def load_staffeli_file(path: str) -> Union[List[Any], Dict[Any, Any]]:
    with open(path, 'r') as f:
        return yaml.load(f)


def find_staffeli_file(
        cachename, searchdir='.', max_depth=MAX_DIR_SEARCH_DEPTH):
    parent = searchdir
    namestr = STAFFELI_FILENAME

    for i in range(max_depth):
        path = _find_file(namestr, parent, max_depth)
        model = load_staffeli_file(path)
        parent = os.path.split(path)[0]
        if len(model) == 1 and cachename in model:
            return parent, model
        parent = os.path.join(parent, '..')

    _raise_lookup_file(namestr, parent)
