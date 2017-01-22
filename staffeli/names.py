from typing import List


def pp(names: List[str]) -> str:
    return "\"{}\"".format("\", \"".join(names))
